#!/usr/bin/env python3
"""Scan all diagnostic fields for a selected car model using PyCanZE.

Lists available vehicles based on the CSV database from the CanZE Android
project. For each ECU field definition it attempts to query the connected
vehicle via a WiFi ELM327 dongle using UDSClient. Retrieved values are printed
to stdout.
"""

from __future__ import annotations

import argparse
import os
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
    # Treat raw logging as orthogonal to scan limits; honor per-ECU limits even when
    # skip-nodata is 0. A "full scan" only relaxes NO_DATA streak behavior.
    full_scan = False

    try:
        frames = load_frames(DATA_DIR)
    except Exception:
        frames = {}

    for field_file in field_files:
        ecu = field_file.stem.replace("_Fields", "")
        if filters and not any(tok == ecu.lower() for tok in filters):
            continue

        ecu_label = ecu if ecu else "_Fields (generic)"
        # Pre-read rows so we can compute the total number of fields available
        rows = list(_read_csv(field_file))
        def _row_counts_as_field(row: list[str]) -> bool:
            try:
                row = (row + [""] * 13)[:13]
                req = row[8]
                if not req or not (req.startswith("22") or req.startswith("21")):
                    return False
                sid = _sid_for_row(row)
                return bool(sid)
            except Exception:
                return False
        total_available = sum(1 for r in rows if _row_counts_as_field(r))
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
                    client.header_settle_ms = max(getattr(client, "header_settle_ms", 0.0) or 0.0, 55.0)
                    # LBC req=0x79B, LBC2 req=0x796
                    client.first_21_delay_by_req[0x79B] = max(
                        client.first_21_delay_by_req.get(0x79B, 0.0) if hasattr(client, "first_21_delay_by_req") else 0.0,
                        160.0,
                    )
                    client.first_21_delay_by_req[0x796] = max(
                        client.first_21_delay_by_req.get(0x796, 0.0) if hasattr(client, "first_21_delay_by_req") else 0.0,
                        150.0,
                    )
                    # Bigger ISO-TP CF window and slightly longer per-CF timeout for long LBC pages
                    # For PH2 (LBC2), use even larger windows to accommodate consistently longer pages
                    if ecu.upper() == "LBC2":
                        client.isotp_collect_timeout_s = max(getattr(client, "isotp_collect_timeout_s", 2.5) or 2.5, 7.5)
                        client.cf_read_timeout_s = max(getattr(client, "cf_read_timeout_s", 1.2) or 1.2, 2.5)
                    else:
                        client.isotp_collect_timeout_s = max(getattr(client, "isotp_collect_timeout_s", 2.5) or 2.5, 6.5)
                        client.cf_read_timeout_s = max(getattr(client, "cf_read_timeout_s", 1.2) or 1.2, 2.3)
                    # Allow wide-CF fallback (ATH1 + ATCF/ATCM 000) if CFs are lost
                    client.wide_cf_fallback = True
                    # Warm-up probe: read a couple robust identifiers to ensure header switch
                    probe_sids = [
                        "7bb.56.6180",
                        "7bb.200.6180",
                        "7bb.16.6101",
                        "7bb.192.6103",
                        "7bb.32.6104",
                    ] if ecu.upper() == "LBC" else [
                        "7b6.56.6180",
                        "7b6.200.6180",
                        "7b6.16.6101",
                        "7b6.192.6103",
                        "7b6.32.6104",
                    ]
                    for ps in probe_sids:
                        try:
                            _ = client.read_field(ps)
                        except Exception:
                            pass
                except Exception:
                    pass
            elif ecu.upper() == "EVC":
                # EVC: prefer ATCRA (some clones miss CFs with mask filters) and
                # allow a small settle time plus slightly larger ISO-TP windows.
                try:
                    client.use_mask_filter = False
                    client.header_settle_ms = max(getattr(client, "header_settle_ms", 0.0) or 0.0, 25.0)
                    client.isotp_collect_timeout_s = max(getattr(client, "isotp_collect_timeout_s", 2.5) or 2.5, 3.5)
                    client.cf_read_timeout_s = max(getattr(client, "cf_read_timeout_s", 1.2) or 1.2, 1.5)
                    # Proactively switch to EVC and try an Extended session; many 0x22 DIDs
                    # on EVC respond more reliably in 0x10 C0. Ignore failures.
                    try:
                        # EVC tester->ECU is 0x7E4, response 0x7EC
                        client._select_frame(0x7E4, 0x7EC)  # type: ignore[attr-defined]
                        client._send("0210C0")  # type: ignore[attr-defined]
                        client._read_lines(1.5)  # type: ignore[attr-defined]
                    except Exception:
                        pass
                except Exception:
                    pass
            elif ecu.upper() in ("USM", "PARKING-SONAR", "UPA", "UPA-ULS"):
                # USM / Parking Sonar: prefer ATCRA and slightly bigger ISO-TP windows; try 0x10C0.
                try:
                    client.use_mask_filter = False
                    client.header_settle_ms = max(getattr(client, "header_settle_ms", 0.0) or 0.0, 30.0)
                    client.isotp_collect_timeout_s = max(getattr(client, "isotp_collect_timeout_s", 2.5) or 2.5, 3.5)
                    client.cf_read_timeout_s = max(getattr(client, "cf_read_timeout_s", 1.2) or 1.2, 1.6)
                    try:
                        # Likely pairs: USM 0x74D->0x76D, UPA 0x74E->0x76E
                        if ecu.upper().startswith("USM"):
                            client._select_frame(0x74D, 0x76D)  # type: ignore[attr-defined]
                        else:
                            client._select_frame(0x74E, 0x76E)  # type: ignore[attr-defined]
                        client._send("0210C0")  # type: ignore[attr-defined]
                        client._read_lines(1.5)  # type: ignore[attr-defined]
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
        # Relax fast-fail if ECU is USM/UPA which may be slow to wake
        max_nodata_without_ok = 20 if ecu.upper() in ("USM", "PARKING-SONAR", "UPA", "UPA-ULS") else 10

        for row in rows:
            # Reset per-iteration transport flags to avoid stale placeholders
            try:
                client.last_positive = False
                client.last_raw_len = 0
                client.last_resp_buf = None
                client.last_status = None
            except Exception:
                pass
            if getattr(args, "per_ecu_limit", 0) and total >= args.per_ecu_limit:
                print(f"-- limit reached ({args.per_ecu_limit} fields), skipping rest of {ecu_label}")
                break
            if getattr(args, "max_secs_per_ecu", 0.0) and (time.time() - start_ecu_ts) > args.max_secs_per_ecu:
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
            # If still unknown to the active dataset, skip this row to avoid
            # printing placeholders based on a previous request buffer.
            if sid_key not in client.fields:
                continue

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
                        same_ecu = not fr or not ecu or (fr.ecu.lower() == ecu.lower())
                        # Don't over-prune for EVC/USM/LBC/LBC2: query fields even if frame map is missing/misnamed
                        if ecu.upper() in ("EVC", "USM", "LBC", "LBC2"):
                            same_ecu = True
                        if not same_ecu:
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
                        # Not expected due to earlier guard; keep explicit reset
                        client.last_positive = False
                        client.last_raw_len = 0
                        value = None
                except BrokenPipeError:
                    return
                except Exception:
                    value = None

            # Treat a transport-positive response (bytes came back) as success.
            # Prefer the presence of a fresh response buffer which is stable across
            # keep-alive calls that may follow inside read_field.
            transport_ok = bool(getattr(client, "last_resp_buf", None))
            if getattr(client, "last_status", None) == "CAN_ERROR":
                reason_counts["CAN_ERROR"] = reason_counts.get("CAN_ERROR", 0) + 1
                if not full_scan:
                    print("Vehicle CAN is asleep (CAN_ERROR). Skipping this ECU.")
                    break
            if getattr(client, "last_status", None) == "NO_DATA":
                reason_counts["NO_DATA"] = reason_counts.get("NO_DATA", 0) + 1
                nodata_streak += 1
                # Fast-fail: if we haven't seen any transport-positive response for this ECU
                # and already hit 10 consecutive NO_DATA, skip the rest of the ECU to save time.
                if ok == 0 and nodata_streak >= max_nodata_without_ok:
                    print(f"No responses from this ECU after {max_nodata_without_ok} NO_DATA. Skipping this ECU.")
                    break
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
                # Prefer showing the decoded value; if None but transport OK, try to decode
                # again from the last positive response buffer before falling back to <bytes>.
                shown = value
                if shown is None:
                    try:
                        fld2 = client.fields.get(sid_key)
                        buf = getattr(client, 'last_resp_buf', None)
                        if fld2 is not None and buf:
                            # Try decoding again from the raw buffer
                            shown = client.decode_value_from_response(fld2, buf)
                            if shown is None:
                                why = getattr(client, 'explain_decode_none', lambda f, r: 'UNKNOWN')(fld2, buf)
                                if why == 'ALL_ONES':
                                    shown = 'n/a'
                                elif why == 'OUT_OF_RANGE':
                                    # One targeted retry with extended timeouts and wide-CF fallback for long pages
                                    # Avoid tight loops by limiting to LBC/LBC2 and large local IDs
                                    try:
                                        ecu_name = ecu.upper() if isinstance(ecu, str) else ""
                                        if ecu_name in ("LBC", "LBC2"):
                                            old_window = getattr(client, 'isotp_collect_timeout_s', 2.5)
                                            old_cf = getattr(client, 'cf_read_timeout_s', 1.2)
                                            old_wide = getattr(client, 'wide_cf_fallback', False)
                                            client.isotp_collect_timeout_s = max(old_window, 5.5)
                                            client.cf_read_timeout_s = max(old_cf, 1.9)
                                            client.wide_cf_fallback = True
                                            try:
                                                retry_val = client.read_field(sid_key)
                                            finally:
                                                client.isotp_collect_timeout_s = old_window
                                                client.cf_read_timeout_s = old_cf
                                                client.wide_cf_fallback = old_wide
                                            if retry_val is not None:
                                                shown = retry_val
                                        if shown is None:
                                            shown = f"<{getattr(client, 'last_raw_len', 0)}B,oor>"
                                    except Exception:
                                        shown = f"<{getattr(client, 'last_raw_len', 0)}B,oor>"
                    except Exception:
                        shown = None
                if shown is None:
                    shown = f"<{getattr(client, 'last_raw_len', 0)}B>"
                print(f" {sid_key:>16} {name} -> {shown}{unit}")
            elif not args.only_values:
                # Show a clearer reason instead of printing raw None
                status = getattr(client, "last_status", None)
                if status in {"NO_DATA", "NEG", "CAN_ERROR", "ELM_ERROR"}:
                    extra = ""
                    if status == "NEG":
                        try:
                            code = getattr(client, "last_nrc_code", None)
                            if isinstance(code, int):
                                extra = f" (NRC 0x{code & 0xFF:02X})"
                        except Exception:
                            pass
                    print(f" {sid_key:>16} {name} -> ({status}){extra}")
                else:
                    # One-time forced reread for LBC/LBC2 to recover cached page and decode
                    recovered = None
                    try:
                        ecu_name = ecu.upper() if isinstance(ecu, str) else ""
                        if ecu_name in ("LBC", "LBC2"):
                            old_win = getattr(client, 'isotp_collect_timeout_s', 2.5)
                            old_cf = getattr(client, 'cf_read_timeout_s', 1.2)
                            client.isotp_collect_timeout_s = max(old_win, 4.5)
                            client.cf_read_timeout_s = max(old_cf, 1.7)
                            try:
                                _ = client.read_field(sid_key)
                                fld2 = client.fields.get(sid_key)
                                buf = getattr(client, 'last_resp_buf', None)
                                if fld2 is not None and buf:
                                    recovered = client.decode_value_from_response(fld2, buf)
                                    if recovered is None:
                                        why = getattr(client, 'explain_decode_none', lambda f, r: 'UNKNOWN')(fld2, buf)
                                        if why == 'ALL_ONES':
                                            recovered = 'n/a'
                                        elif why == 'OUT_OF_RANGE':
                                            recovered = f"<{getattr(client, 'last_raw_len', 0)}B,oor>"
                            finally:
                                client.isotp_collect_timeout_s = old_win
                                client.cf_read_timeout_s = old_cf
                    except Exception:
                        recovered = None
                    if recovered is not None:
                        ok += 1
                        unit = ""
                        try:
                            fld2 = client.fields.get(sid_key)
                            if fld2 and fld2.unit:
                                unit = f" {fld2.unit}"
                        except Exception:
                            pass
                        print(f" {sid_key:>16} {name} -> {recovered}{unit}")
                    else:
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
        print(f"-- {ecu_label}: {ok}/{total_available} values{suffix}")


def main() -> None:
    args = parse_args()
    car = args.car or prompt_for_car()
    # Align the UDS dataset with the selected car for accurate field maps
    try:
        os.environ["PYCANZE_VEHICLE"] = car
    except Exception:
        pass
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

