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
    from pycanze.parser import _read_csv, load_frames, load_ecus  # type: ignore
    from pycanze.uds import ELM_CMD_SLEEP  # type: ignore
except ModuleNotFoundError:
    # Allow running directly from the repo without installing the package
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from pycanze import UDSClient  # type: ignore
    from pycanze.parser import _read_csv, load_frames, load_ecus  # type: ignore
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
    # Load ECU metadata to enrich headers with a short description
    ecu_desc_map: dict[str, str] = {}
    try:
        ecus = load_ecus(DATA_DIR, vehicle=car)
        for _sid, e in ecus.items():
            try:
                desc = (e.name or "").strip()
            except Exception:
                desc = ""
            if not desc:
                continue
            # Index by mnemonic and aliases (upper-cased for case-insensitive match)
            try:
                if e.mnemonic:
                    ecu_desc_map.setdefault(e.mnemonic.upper(), desc)
            except Exception:
                pass
            try:
                for al in (e.aliases or []):
                    if al:
                        ecu_desc_map.setdefault(al.upper(), desc)
            except Exception:
                pass
    except Exception:
        pass
    # Fallback static descriptions for common ECUs when CSV lacks detail
    static_desc = {
        "EVC": "Electric Vehicle Controller (gateway)",
        "LBC": "Lithium Battery Controller",
        "LBC2": "Battery Controller (phase 2)",
        "EPS": "Electric Power Steering",
        "DCM": "Telematics/Connectivity module",
        "BCB-OBC": "On-board charger",
        "USM": "Ultrasonic sensor module",
        "UPA": "Parking assistance",
    }

    # Build a cached ECU -> list of SID keys index from the already loaded dataset
    # to avoid re-reading CSV files per ECU. Fields come from UDSClient (parser lru_cache).
    ecu_to_sids: dict[str, list[str]] = {}
    generic_sids: list[str] = []
    try:
        for sid_key, fld in getattr(client, "fields", {}).items():
            try:
                fid = getattr(fld, "frame_id", 0)
                fr = frames.get(fid) if frames else None
                if fr and getattr(fr, "ecu", None):
                    ecu_to_sids.setdefault(fr.ecu, []).append(sid_key)
                else:
                    # Fallback grouping by well-known frame ids when frame->ECU map is missing
                    if isinstance(fid, int):
                        if fid == 0x7BB:
                            ecu_to_sids.setdefault("LBC", []).append(sid_key)
                            continue
                        if fid == 0x7B6:
                            ecu_to_sids.setdefault("LBC2", []).append(sid_key)
                            continue
                    generic_sids.append(sid_key)
            except Exception:
                generic_sids.append(sid_key)
    except Exception:
        pass

    for field_file in field_files:
        ecu = field_file.stem.replace("_Fields", "")
        if filters and not any(tok == ecu.lower() for tok in filters):
            continue

        ecu_label = ecu if ecu else "_Fields (generic)"
        # Use the cached ECU->SID mapping instead of re-reading CSV files
        if ecu:
            sids_for_ecu = ecu_to_sids.get(ecu, [])
        else:
            sids_for_ecu = generic_sids
        total_available = len(sids_for_ecu)
        # Try to show a short description for this ECU
        desc = None
        try:
            key = ecu.upper()
            desc = ecu_desc_map.get(key) or static_desc.get(key)
        except Exception:
            desc = None
        if desc:
            print(f"\nECU: {ecu_label} - {desc}")
        else:
            print(f"\nECU: {ecu_label}")
        # Optional, throttled EVC gateway poke once per ECU (disabled by default; enable by setting PYCANZE_DISABLE_GATEWAY_POKE=0)
        if os.environ.get("PYCANZE_DISABLE_GATEWAY_POKE", "1").strip() not in ("1", "true", "True"):
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
        nodata_reqs: dict[str, str] = {}  # track by sid_key with last status to avoid repeated queries
        neg_reqs: set[str] = set()
        ensured_session = False
        # Known UDS service names for clearer unsupported reason printing
        uds_service_names = {
            0x10: "DiagnosticSessionControl",
            0x14: "ClearDiagnosticInformation",
            0x19: "ReadDiagnosticTroubleCodeInformation",
            0x23: "ReadMemoryByAddress",
            0x27: "SecurityAccess",
            0x2E: "WriteDataByIdentifier",
            0x2F: "IOControl",
            0x31: "RoutineControl",
            0x34: "RequestDownload",
            0x36: "TransferData",
            0x37: "RequestTransferExit",
            0x3E: "TesterPresent",
            0x85: "ControlDTCSetting",
        }
        # Use the CLI --skip-nodata threshold for fast-fail too; allow a gentler value for slow ECUs
        max_nodata_without_ok = int(getattr(args, "skip_nodata", 50) or 0)
        # Apply a hard time budget for this ECU inside UDSClient when supported
        try:
            if getattr(args, "max_secs_per_ecu", 0.0):
                client._deadline_ts = start_ecu_ts + float(args.max_secs_per_ecu)
            else:
                client._deadline_ts = None
        except Exception:
            pass

        for sid_key in sids_for_ecu:
            # Reset per-iteration transport flags to avoid stale placeholders
            try:
                client.last_positive = False
                client.last_raw_len = 0
                client.last_resp_buf = None
                client.last_status = None
            except Exception:
                pass

            issued_req = False
            if getattr(args, "per_ecu_limit", 0) and total >= args.per_ecu_limit:
                print(f"-- limit reached ({args.per_ecu_limit} fields), skipping rest of {ecu_label}")
                break
            if getattr(args, "max_secs_per_ecu", 0.0) and (time.time() - start_ecu_ts) > args.max_secs_per_ecu:
                print(f"-- time budget reached ({args.max_secs_per_ecu:.0f}s), skipping rest of {ecu_label}")
                break

            # sid_key already provided by index; fetch field meta
            sid_key = str(sid_key).lower()
            fld = client.fields.get(sid_key)
            name = getattr(fld, "name", sid_key)

            # Classify UDS service; only 0x21/0x22 are read-supported
            svc = None
            try:
                rid = (fld.request_id or "").upper()
                svc = int(rid[:2], 16) if len(rid) >= 2 else None
            except Exception:
                svc = None

            if svc not in (0x21, 0x22):
                svc_name = uds_service_names.get(svc, "UnknownService")
                if svc is None:
                    label = "UNSUPPORTED: (invalid or missing RequestId)"
                else:
                    label = f"UNSUPPORTED: 0x{svc:02X} {svc_name}"
                # Keep counts under a generic bucket; summaries currently only include transport reasons
                reason_counts["UNSUPPORTED"] = 1 + reason_counts.get("UNSUPPORTED", 0)
                # Remember per-SID reason so we don’t re-query and can reprint the detail later
                nodata_reqs[sid_key] = label
                if not args.only_values:
                    print(f" {sid_key:>16} {name} -> ({label})")
                continue

            # If still unknown to the active dataset, skip this row to avoid
            # printing placeholders based on a previous request buffer.
            # Already ensured fld_meta exists above

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

            if (sid_key in nodata_reqs or sid_key in neg_reqs) and ecu.upper() not in ("LBC", "LBC2"):
                value = None
                if sid_key in neg_reqs:
                    client.last_status = "NEG"
                else:
                    # Reuse the last recorded NO_DATA variant for accurate reason reporting
                    client.last_status = nodata_reqs.get(sid_key, "NO_DATA")
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
                            issued_req = True
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
            status = getattr(client, "last_status", None)
            if status == "CAN_ERROR":
                reason_counts["CAN_ERROR"] = reason_counts.get("CAN_ERROR", 0) + 1
                if not full_scan:
                    print("Vehicle CAN is asleep (CAN_ERROR). Skipping this ECU.")
                    break
            if status in ("NO_DATA", "NO_DATA_TIMEOUT", "NO_DATA_ADAPTER"):
                key = "NO_DATA_TIMEOUT" if status == "NO_DATA_TIMEOUT" else ("NO_DATA_ADAPTER" if status == "NO_DATA_ADAPTER" else "NO_DATA")
                reason_counts[key] = reason_counts.get(key, 0) + 1
                nodata_streak += 1
                # Fast-fail and hard limit are unified via max_nodata_without_ok
                threshold = max_nodata_without_ok
                if threshold > 0 and nodata_streak >= threshold:
                    print(f"Too many NO_DATA in a row ({nodata_streak}). Skipping this ECU.")
                    break
                nodata_reqs[sid_key] = key
            elif status == "ELM_ERROR":
                reason_counts["ELM_ERROR"] = reason_counts.get("ELM_ERROR", 0) + 1
            elif status == "NEG":
                reason_counts["NEG"] = reason_counts.get("NEG", 0) + 1
                neg_reqs.add(sid_key)
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
                if status in {"NO_DATA", "NO_DATA_TIMEOUT", "NO_DATA_ADAPTER", "NEG", "CAN_ERROR", "ELM_ERROR"}:
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
                    # If previously marked unsupported, reprint its detailed reason
                    try:
                        detail = nodata_reqs.get(sid_key)
                    except Exception:
                        detail = None
                    if isinstance(detail, str) and detail.startswith("UNSUPPORTED"):
                        print(f" {sid_key:>16} {name} -> ({detail})")
                        continue
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
                                issued_req = True
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
                        # If we never issued a request, this was skipped; otherwise decoding produced no usable value.
                        label = "(SKIPPED)" if not issued_req else "(DECODE_NA)"
                        print(f" {sid_key:>16} {name} -> {label}")

        if reason_counts:
            parts: list[str] = []
            for k in ("NO_DATA", "NO_DATA_TIMEOUT", "NO_DATA_ADAPTER", "NEG", "CAN_ERROR", "ELM_ERROR"):
                if k in reason_counts:
                    if k == "NEG" and nrc_seen:
                        nrcs = ",".join(f"0x{c:02X}" for c in sorted(nrc_seen))
                        parts.append(f"{k}={reason_counts[k]} (NRCs: {nrcs})")
                    else:
                        parts.append(f"{k}={reason_counts[k]}")
            suffix = f"; reasons: {'; '.join(parts)}" if parts else ""
        else:
            suffix = ""
        elapsed = time.time() - start_ecu_ts
        print(f"-- {ecu_label}: {ok}/{total_available} values in {elapsed:.1f}s{suffix}")
        # Clear any deadline to avoid affecting the next ECU
        try:
            client._deadline_ts = None
        except Exception:
            pass


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

