#!/usr/bin/env python3
"""Scan all diagnostic fields for a selected car model using PyCanZE.

Lists available vehicles based on the CSV database from the CanZE Android
project. For each ECU field definition it attempts to query the connected
vehicle via a WiFi ELM327 dongle using UDSClient. Retrieved values are printed
to stdout.
"""

from __future__ import annotations

import argparse
import socket
import sys
import time
from pathlib import Path

try:
    from pycanze import UDSClient  # type: ignore
    from pycanze.parser import _read_csv, load_frames  # type: ignore
    from pycanze.uds import ELM_CMD_SLEEP  # type: ignore
except ModuleNotFoundError:
    # Allow running directly from the repo without installing the package
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from pycanze import UDSClient  # type: ignore
    from pycanze.parser import _read_csv, load_frames  # type: ignore
    from pycanze.uds import ELM_CMD_SLEEP  # type: ignore

# Directory containing copied asset CSV files
DATA_DIR = Path(__file__).resolve().parent / "data"


def list_cars() -> list[str]:
    return sorted([d.name for d in DATA_DIR.iterdir() if d.is_dir()])


def parse_args() -> argparse.Namespace:
    cars = list_cars()
    p = argparse.ArgumentParser(description="Scan ECU data points for a car")
    p.add_argument("car", nargs="?", choices=cars, help="Car model to scan")
    p.add_argument("--host", default="192.168.2.21", help="ELM327 host")
    p.add_argument("--port", type=int, default=35000, help="ELM327 TCP port")
    p.add_argument("--ecu", action="append", help="Filter to ECUs (repeatable)")
    p.add_argument("--only-values", action="store_true", help="Print only values")
    p.add_argument("--elm-timeout", type=float, default=3.0, help="ELM prompt timeout (s)")
    p.add_argument("--skip-nodata", type=int, default=50, help="Skip ECU after this many NO_DATA in a row (0=disable)")
    p.add_argument("--per-ecu-limit", type=int, default=0, help="Max fields per ECU (0=no limit)")
    p.add_argument("--max-secs-per-ecu", type=float, default=600.0, help="Max seconds per ECU (0=no limit)")
    p.add_argument("--raw-log", type=Path, help="File to store raw ELM327 traffic")
    return p.parse_args()


def prompt_for_car() -> str:
    cars = list_cars()
    if not cars:
        raise SystemExit("No car definitions found under data directory")
    print("Available cars:")
    for idx, car in enumerate(cars, start=1):
        print(f"{idx}. {car}")
    while True:
        try:
            choice = int(input(f"Select car [1-{len(cars)}]: "))
            if 1 <= choice <= len(cars):
                return cars[choice - 1]
        except ValueError:
            pass
        print("Invalid selection. Please try again.")


def _sid_for_row(row: list[str]) -> str | None:
    # Normalize row length like the parser
    row = (row + [""] * 13)[:13]
    sid, frame_id_s, start_bit_s, _end_bit_s, _resolution_s, _offset_s, _decimals_s, _unit, _request_id, response_id, _options_s, _name, _raw_values = row
    sid = sid.strip()
    if sid and not sid.startswith("#"):
        return sid
    if not frame_id_s or not start_bit_s or not response_id:
        return None
    return f"{frame_id_s}.{start_bit_s}.{response_id}"


def scan_car(car: str, client: UDSClient) -> None:
    car_dir = DATA_DIR / car
    field_files = sorted(f for f in car_dir.iterdir() if f.name.endswith("_Fields.csv"))
    if not field_files:
        print(f"No field definitions found for {car}")
        return

    args = parse_args()
    filters = [t.lower() for t in (args.ecu or [])]
    full_scan = (getattr(args, "skip_nodata", 50) == 0) or bool(getattr(args, "raw_log", None))

    try:
        frames = load_frames(DATA_DIR)
    except Exception:
        frames = {}

    for field_file in field_files:
        ecu = field_file.stem.replace("_Fields", "")
        if filters and not any(tok in ecu.lower() for tok in filters):
            continue
        ecu_label = ecu if ecu else "_Fields (generic)"
        print(f"\nECU: {ecu_label}")
        try:
            client.gateway_poke()
        except Exception:
            pass
        try:
            client.use_mask_filter = True
            # Some ELM clones drop CFs for LBC/LBC2 when using ATCF/ATCM.
            # Prefer exact ATCRA filtering for these ECUs to improve reliability.
            if ecu.upper() in ("LBC", "LBC2"):
                client.use_mask_filter = False
                try:
                    # Increase header settle and first-0x21 delays for LBC/LBC2
                    client.header_settle_ms = max(getattr(client, "header_settle_ms", 0.0) or 0.0, 45.0)
                    # LBC req=0x79B, LBC2 req=0x796
                    client.first_21_delay_by_req[0x79B] = max(
                        client.first_21_delay_by_req.get(0x79B, 0.0) if hasattr(client, "first_21_delay_by_req") else 0.0,
                        150.0,
                    )
                    client.first_21_delay_by_req[0x796] = max(
                        client.first_21_delay_by_req.get(0x796, 0.0) if hasattr(client, "first_21_delay_by_req") else 0.0,
                        120.0,
                    )
                    # Warm-up probe: read a couple robust identifiers to ensure header switch
                    probe_sids = [
                        "7bb.56.6180",
                        "7bb.200.6180",
                        "7bb.16.6101",
                        "7bb.192.6103",
                        "7bb.32.6104",
                    ] if ecu.upper() == "LBC" else [
                        "7b6.56.6180",
                    ]
                    for ps in probe_sids:
                        try:
                            _ = client.read_field(ps)
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception:
            pass

        ok = 0
        total = 0
        nodata_streak = 0
        start_ecu_ts = time.time()
        reason_counts: dict[str, int] = {}
        nrc_seen: set[int] = set()
        nodata_reqs: set[str] = set()
        neg_reqs: set[str] = set()
        ensured_session = False

        for row in _read_csv(field_file):
            if (not full_scan) and getattr(args, "per_ecu_limit", 0) and total >= args.per_ecu_limit:
                print(f"-- limit reached ({args.per_ecu_limit} fields), skipping rest of {ecu_label}")
                break
            if (not full_scan) and getattr(args, "max_secs_per_ecu", 0.0) and (time.time() - start_ecu_ts) > args.max_secs_per_ecu:
                print(f"-- time budget reached ({args.max_secs_per_ecu:.0f}s), skipping rest of {ecu_label}")
                break

            sid = _sid_for_row(row)
            if not sid:
                continue
            sid_key = sid.lower()
            req = (row + [""] * 13)[8]
            if not req or not (req.startswith("22") or req.startswith("21")):
                continue
            name = (row + [""] * 12)[11]

            if sid_key not in client.fields:
                try:
                    parts = sid_key.split(".")
                    if len(parts) == 3 and all(parts):
                        alt = f"{parts[0]}.{parts[2]}.{parts[1]}"
                        if alt in client.fields:
                            sid_key = alt
                except Exception:
                    pass

            if not ensured_session and sid_key in client.fields:
                try:
                    f = client.fields[sid_key]
                    same_ecu = True
                    try:
                        fr = frames.get(getattr(f, "frame_id", 0))
                        if fr and ecu:
                            same_ecu = (fr.ecu.lower() == ecu.lower())
                    except Exception:
                        same_ecu = True
                    if same_ecu:
                        try:
                            req_id, _resp_id = client._pair_for_frame(getattr(f, "frame_id", 0))  # type: ignore[attr-defined]
                            client.header_settle_ms = max(getattr(client, "header_settle_ms", 0.0) or 0.0, 35.0)
                            client.first_21_delay_by_req[req_id] = max(
                                client.first_21_delay_by_req.get(req_id, 0.0) if hasattr(client, "first_21_delay_by_req") else 0.0,
                                80.0,
                            )
                            client.use_mask_filter = bool(req_id > 0x7FF)
                            if req_id in (0x7CA, 0x18DAF110):
                                client.header_settle_ms = max(client.header_settle_ms, 45.0)
                                client.first_21_delay_by_req[req_id] = max(
                                    client.first_21_delay_by_req.get(req_id, 0.0), 120.0
                                )
                                try:
                                    client.prime_ecu(getattr(f, "frame_id", 0))
                                except Exception:
                                    pass
                            if req_id in (0x79B,):
                                client.header_settle_ms = max(client.header_settle_ms, 40.0)
                                client.first_21_delay_by_req[req_id] = max(
                                    client.first_21_delay_by_req.get(req_id, 0.0), 100.0
                                )
                                try:
                                    client.prime_ecu(getattr(f, "frame_id", 0))
                                except Exception:
                                    pass
                        except Exception:
                            pass
                        client.ensure_session(f.frame_id, force=True)
                        ensured_session = True
                except Exception:
                    pass

            if req and (req in nodata_reqs or req in neg_reqs) and ecu.upper() not in ("LBC", "LBC2"):
                value = None
                client.last_status = "NEG" if req in neg_reqs else "NO_DATA"
            else:
                try:
                    fld = client.fields.get(sid_key)
                    if fld is not None:
                        fr = frames.get(getattr(fld, "frame_id", 0)) if frames else None
                        if fr and ecu and fr.ecu.lower() != ecu.lower():
                            value = None
                        else:
                            value = client.read_field(sid_key)
                            if getattr(client, "last_status", None) == "NEG":
                                try:
                                    code = getattr(client, "last_nrc_code", None)
                                    if isinstance(code, int):
                                        nrc_seen.add(code & 0xFF)
                                except Exception:
                                    pass
                    else:
                        value = None
                except BrokenPipeError:
                    return
                except Exception:
                    value = None

            # Treat a transport-positive response (bytes came back) as success
            transport_ok = bool(getattr(client, "last_positive", False))
            if getattr(client, "last_status", None) == "CAN_ERROR":
                reason_counts["CAN_ERROR"] = reason_counts.get("CAN_ERROR", 0) + 1
                if not full_scan:
                    print("Vehicle CAN is asleep (CAN_ERROR). Skipping this ECU.")
                    break
            if getattr(client, "last_status", None) == "NO_DATA":
                reason_counts["NO_DATA"] = reason_counts.get("NO_DATA", 0) + 1
                nodata_streak += 1
                threshold = getattr(args, "skip_nodata", 50)
                if threshold > 0 and nodata_streak >= threshold:
                    print(f"Too many NO_DATA in a row ({nodata_streak}). Skipping this ECU.")
                    break
                if req:
                    nodata_reqs.add(req)
            elif getattr(client, "last_status", None) == "ELM_ERROR":
                reason_counts["ELM_ERROR"] = reason_counts.get("ELM_ERROR", 0) + 1
            elif getattr(client, "last_status", None) == "NEG":
                reason_counts["NEG"] = reason_counts.get("NEG", 0) + 1
                if req:
                    neg_reqs.add(req)
            else:
                nodata_streak = 0

            total += 1
            if value is not None or transport_ok:
                ok += 1
                unit = ""
                try:
                    fld2 = client.fields.get(sid_key)
                    if fld2 and fld2.unit:
                        unit = f" {fld2.unit}"
                except Exception:
                    pass
                # Prefer showing the decoded value; if None but transport OK, hint with "<bytes>"
                shown = value if value is not None else f"<{getattr(client, 'last_raw_len', 0)}B>"
                print(f" {sid_key:>16} {name} -> {shown}{unit}")
            elif not args.only_values:
                print(f" {sid_key:>16} {name} -> {value}")

        if reason_counts:
            parts: list[str] = []
            for k in ("NO_DATA", "NEG", "CAN_ERROR", "ELM_ERROR"):
                if k in reason_counts:
                    if k == "NEG" and nrc_seen:
                        nrcs = ",".join(f"0x{c:02X}" for c in sorted(nrc_seen))
                        parts.append(f"{k}={reason_counts[k]} (NRCs: {nrcs})")
                    else:
                        parts.append(f"{k}={reason_counts[k]}")
            suffix = f"; reasons: {'; '.join(parts)}" if parts else ""
        else:
            suffix = ""
        print(f"-- {ecu_label}: {ok}/{total} values{suffix}")


def main() -> None:
    args = parse_args()
    car = args.car or prompt_for_car()
    client = UDSClient(args.host, port=args.port, timeout=args.elm_timeout)
    try:
        client.header_settle_ms = max(getattr(client, "header_settle_ms", 0.0) or 0.0, 10.0)
        client.delay_before_21_ms = max(getattr(client, "delay_before_21_ms", 0.0) or 0.0, 10.0)
        client.wide_cf_fallback = True
        client.use_mask_filter = True
    except Exception:
        pass

    log_fh = None
    if getattr(args, "raw_log", None):
        log_fh = open(args.raw_log, "w", encoding="utf-8")
        orig_send = client._send
        orig_read = client._read_lines

        def logged_send(line: str, wait: float = ELM_CMD_SLEEP) -> None:
            log_fh.write(f"> {line}\n")
            log_fh.flush()
            orig_send(line, wait)

        def logged_read_lines(timeout: float | None = None):
            lines = orig_read(timeout)
            for l in lines:
                log_fh.write(f"< {l}\n")
            log_fh.flush()
            return lines

        client._send = logged_send  # type: ignore[assignment]
        client._read_lines = logged_read_lines  # type: ignore[assignment]
    try:
        try:
            client.connect()
        except (OSError, ConnectionError, socket.timeout) as e:
            print(f"ELM327 not reachable at {args.host}:{args.port} -> {e}")
            sys.exit(2)
        try:
            client.initialize()
        except Exception as e:
            print(f"ELM327 initialization failed -> {e}")
            sys.exit(3)
        scan_car(car, client)
    finally:
        if log_fh:
            log_fh.close()
        client.close()

    print(f"Finished scanning {car}")


if __name__ == "__main__":
    main()

