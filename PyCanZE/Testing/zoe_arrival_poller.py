#!/usr/bin/env python3
# zoe_arrival_poller.py — laptop-first poller for Renault ZOE + ELM327 WiFi dongle
# - Pings the dongle every 30s (configurable).
# - On first successful ping, connects to ELM327 and rapidly polls SoC (0x2002) and Odometer (0x2006)
#   until both are captured once. Then it switches to a slow 5 min cadence while the dongle is reachable.
# - Prints everything to stdout (no MQTT). Clean exit on Ctrl+C.
#
# Tested with: ELM327 WiFi clones that speak ASCII "AT" protocol on TCP port 35000 / 23 / 3501 (set below).
#
# Usage:
#   python3 zoe_arrival_poller.py
#
# Tip: First run your existing dongle self-test to confirm basics before using this poller.
#      Adjust ELM_HOST and ELM_PORT below.
#
# Notes:
# - Works best when the ZOE is "wakker" (Ready or charger plugged). While asleep, UDS may not answer.
# - Cross-platform ping: uses `ping` subprocess (Windows vs POSIX flags handled).
#
# MIT License — do as you like. :)

import sys, socket, time, subprocess, platform, re
from datetime import datetime
import json
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import os
import argparse
from datetime import datetime, timedelta

# ----------------- Configuration -----------------
ELM_HOST = "192.168.2.21"   # IP of your WiFi ELM327 dongle
ELM_PORT = 35000            # Typical ports: 35000, 3501, 23
ELM_TIMEOUT_S = 12.0
ELM_CMD_SLEEP = 0.12        # Delay after sending an AT/UDS line (seconds)

PING_INTERVAL_IDLE = 30     # seconds when dongle unreachable
FAST_POLL_INTERVAL = 3      # seconds while trying to capture first SoC+Odo
FAST_POLL_MAX_WINDOW = 180  # seconds (3 min) max to stay in fast mode
SLOW_POLL_INTERVAL = 300    # seconds (5 min) while dongle stays reachable

# UDS identifiers
REQ_ID = "7E4"
RSP_ID = "7EC"
DID_SOC = (0x20, 0x02)
DID_ODO = (0x20, 0x06)

HEX2 = re.compile(r"[0-9A-Fa-f]{2}")
DIGIT_HEX = set("0123456789abcdefABCDEF")

VERBOSE = False

# Charging/schedule config
TARGET_SOC_PERCENT = 70.0       # desired SoC at target time
TARGET_TIME_HH_MM = "07:30"     # daily target time (local)
CHARGE_RATE_PCT_PER_HOUR = 6.15 # ≈ 13A at 230V single-phase → ~6.15%/h (tune as needed)

# Shelly switch (charger) config
SHELLY_ENABLED = True
SHELLY_HOST = "192.168.2.14"    # Shelly IP
SHELLY_POLL_INTERVAL = 30       # seconds
AUTO_SHELLY = False             # if True, will attempt to turn on at planned start time

# State machine
STATE_WAIT_DONGLE = "WAIT_DONGLE"
STATE_FAST_CAPTURE = "FAST_CAPTURE"
STATE_SLOW_MONITOR = "SLOW_MONITOR"

# ----------------- Logging helpers -----------------
def now_ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg):
    print(f"[{now_ts()}] {msg}", flush=True)

def debug(msg):
    if VERBOSE:
        print(f"[DEBUG] {msg}", flush=True)

# ----------------- Ping helper -----------------
def ping_host(host, timeout_s=1.0):
    """
    Returns True if host answers a single ICMP ping within timeout.
    Uses system ping for portability.
    """
    is_windows = platform.system().lower().startswith("win")
    if is_windows:
        # -n 1 (one echo); -w timeout in ms
        cmd = ["ping", "-n", "1", "-w", str(int(timeout_s * 1000)), host]
    else:
        # -c 1 (one echo); -W timeout in seconds (BusyBox/OSX variants differ; this is common on Linux)
        cmd = ["ping", "-c", "1", "-W", str(int(round(timeout_s))), host]

    try:
        proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        return proc.returncode == 0
    except Exception:
        return False

# ----------------- ELM327 helpers -----------------
def _send(sock, line, wait=ELM_CMD_SLEEP):
    debug(f"SEND: {line}")
    sock.sendall((line + "\r").encode("ascii", errors="ignore"))
    time.sleep(wait)

def _read_lines(sock, timeout=ELM_TIMEOUT_S):
    sock.settimeout(timeout)
    buf = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf += chunk
        if b">" in buf:
            break
    text = buf.decode(errors="ignore").replace("\r", "\n")
    debug(f"RAW RECV: {repr(text)}")
    lines = [ln.strip() for ln in text.split("\n") if ln.strip() and ln.strip() != ">"]
    debug(f"RECV: {lines}")
    return lines

def _only_hex_bytes(lines):
    """
    Extract all hex bytes from lines, tolerant to glued hex (e.g. '0662200600B5FBAA').
    Filters out 'NO DATA', 'ERROR', etc.
    """
    out = []
    for ln in lines:
        up = ln.upper()
        if any(k in up for k in ["NO DATA","ERROR","SEARCHING","BUS INIT","CAN ERROR"]):
            continue
        # Remove non-hex chars, then split every 2 chars
        only_hex = "".join(ch for ch in ln if ch.upper() in "0123456789ABCDEF")
        pairs = HEX2.findall(only_hex)
        out += [p.upper() for p in pairs]
    return [int(b, 16) for b in out]

def elm_init(sock):
    """ELM init matching selftest script (no ATCEA/ATST, longer sleep after ATZ)."""
    _send(sock, "ATZ", wait=0.3)
    _ = _read_lines(sock, timeout=3.0)
    for cmd in ("ATE0", "ATS0", "ATSP6", "ATAT1", "ATCAF0"):
        _send(sock, cmd)
        _ = _read_lines(sock, timeout=3.0)
    # Headers
    _send(sock, "ATSH7E4"); _read_lines(sock, 3.0)
    _send(sock, "ATFCSH7E4"); _read_lines(sock, 3.0)
        # Removed ATCEA 00 and ATST FF to match selftest

def set_ids(sock):
    _send(sock, f"ATSH7E4"); _read_lines(sock, 3.0)
    _send(sock, f"ATFCSH7E4"); _read_lines(sock, 3.0)
    _send(sock, f"ATCRA {RSP_ID}"); _read_lines(sock, 3.0)

def clear_ids(sock):
    _send(sock, "ATCRA 000"); _read_lines(sock, 3.0)

def uds_rdbi(sock, did_hi, did_lo):
    """UDS ReadDataByIdentifier using exact raw command as in selftest (0322DID).
    Tolerant parse: find 62 DID_HI DID_LO anywhere in the response and return the following bytes.
    Returns None for negative responses (0x7F ...).
    """
    cmd = f"0322{did_hi:02X}{did_lo:02X}"
    debug(f"RAW UDS CMD: {cmd}")
    _send(sock, cmd)
    lines = _read_lines(sock)
    b = _only_hex_bytes(lines)
    debug(f"PARSED HEX: {b}")
    # Negative response handling
    for i in range(0, max(0, len(b) - 2)):
        if b[i] == 0x7F and (i + 2) < len(b):
            debug(f"NEGATIVE RESPONSE 0x7F for service 0x{b[i+1]:02X}, code 0x{b[i+2]:02X}")
            return None
    # Find the positive response marker anywhere
    for i in range(0, max(0, len(b) - 2)):
        if b[i] == 0x62 and b[i+1] == did_hi and b[i+2] == did_lo:
            payload = b[i+3:]
            debug(f"MATCH at {i}, payload={payload}")
            return payload
    return None

def decode_soc(payload):
    """Return SoC in % if payload present (2 bytes, big-endian, scale 0.02%).
    Treat raw==0 as no data (car likely asleep), to avoid false 0.00%.
    """
    if payload and len(payload) >= 2:
        raw = (payload[0] << 8) | payload[1]
        if raw == 0:
            return None
        return (raw * 2) / 100.0
    return None

def decode_odo(payload):
    """Return odometer in km (3 bytes big-endian)."""
    if payload and len(payload) >= 3:
        return float((payload[0] << 16) | (payload[1] << 8) | payload[2])
    return None

# ----------------- Poll cycles -----------------
def try_poll_once():
    """Connects to ELM, tries to read SoC and Odo once. Returns tuple (soc, km). Each request uses a fresh connection, matching selftest."""
    # Poll SoC
    with socket.create_connection((ELM_HOST, ELM_PORT), timeout=ELM_TIMEOUT_S) as s:
        elm_init(s)
        soc_p = uds_rdbi(s, *DID_SOC)
    # Poll Odo
    with socket.create_connection((ELM_HOST, ELM_PORT), timeout=ELM_TIMEOUT_S) as s:
        elm_init(s)
        odo_p = uds_rdbi(s, *DID_ODO)

    soc = decode_soc(soc_p) if soc_p is not None else None
    km  = decode_odo(odo_p) if odo_p is not None else None

    if soc is not None:
        raw = " ".join(f"{b:02X}" for b in (soc_p or []))
        log(f"SoC  = {soc:.2f}%   (raw {raw})")
    else:
        log("SoC  = (no data)")
    if km is not None:
        raw = " ".join(f"{b:02X}" for b in (odo_p or []))
        log(f"Odo  = {km:.0f} km (raw {raw})")
    else:
        log("Odo  = (no data)")

    return soc, km

def _next_target_datetime(hh_mm: str):
    now = datetime.now()
    try:
        hh, mm = [int(x) for x in hh_mm.split(":", 1)]
    except Exception:
        hh, mm = 7, 30
    target = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if target <= now:
        # move to next day
        from datetime import timedelta
        target = target + timedelta(days=1)
    return target

def _compute_charge_plan(current_soc: float, target_soc: float, target_time_str: str, rate_pct_per_hour: float):
    target_dt = _next_target_datetime(target_time_str)
    needed = max(0.0, target_soc - current_soc)
    hours_needed = needed / max(0.001, rate_pct_per_hour)
    from datetime import timedelta
    start_at = target_dt - timedelta(hours=hours_needed)
    return {
        "measured_soc": current_soc,
        "target_soc": target_soc,
        "target_dt": target_dt,
        "needed_pct": needed,
        "hours_needed": hours_needed,
        "start_at": start_at,
    }

# -------- Shelly helpers (best-effort, tolerant to model differences) --------

def shelly_get_state():
    if not SHELLY_ENABLED:
        return None
    urls = [
        f"http://{SHELLY_HOST}/relay/0",
        f"http://{SHELLY_HOST}/status",
    ]
    headers = {"Accept": "application/json"}
    for u in urls:
        try:
            debug(f"SHELLY GET {u}")
            with urlopen(Request(u, headers=headers), timeout=2.0) as r:
                raw = r.read().decode("utf-8", errors="ignore")
                debug(f"SHELLY RECV: {raw}")
                try:
                    data = json.loads(raw)
                except Exception:
                    # some firmwares return plain 'on'/'off'
                    txt = raw.strip().lower()
                    if txt in ("on", "off"):
                        return txt == "on"
                    continue
                # Try common locations
                if "ison" in data:
                    return bool(data.get("ison"))
                if isinstance(data, dict) and "relays" in data and data["relays"]:
                    return bool(data["relays"][0].get("ison"))
        except (URLError, HTTPError, TimeoutError, ConnectionError, OSError) as e:
            debug(f"SHELLY ERR: {e}")
            continue
    return None

def shelly_set(on: bool):
    if not SHELLY_ENABLED:
        return False
    try:
        action = "on" if on else "off"
        url = f"http://{SHELLY_HOST}/relay/0?turn={action}"
        debug(f"SHELLY SET {url}")
        with urlopen(url, timeout=2.0) as r:
            _ = r.read()
        return True
    except Exception as e:
        debug(f"SHELLY SET ERR: {e}")
        return False

# Persistence
DEFAULT_STATE_FILE = os.path.join(os.getcwd(), "zoe_poller_state.json")

def _dt_to_iso(dt: datetime | None):
    return dt.isoformat() if isinstance(dt, datetime) else None

def _iso_to_dt(s: str | None):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

def load_state(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Normalize
        if "plan" in data and data["plan"]:
            p = data["plan"]
            p["target_dt"] = _iso_to_dt(p.get("target_dt"))
            p["start_at"] = _iso_to_dt(p.get("start_at"))
        return data
    except Exception:
        return {}

def save_state(path: str, data: dict):
    try:
        out = dict(data)
        p = out.get("plan")
        if p:
            p = dict(p)
            p["target_dt"] = _dt_to_iso(p.get("target_dt"))
            p["start_at"] = _dt_to_iso(p.get("start_at"))
            out["plan"] = p
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
    except Exception as e:
        debug(f"SAVE STATE ERR: {e}")

def main():
    global VERBOSE
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--state-file", default=DEFAULT_STATE_FILE)
    parser.add_argument("--no-plan", action="store_true", help="Schakel plannen uit (geen nieuw laadplan aanmaken en geen AUTO_SHELLY acties)")
    parser.add_argument("--target-soc", type=float, default=TARGET_SOC_PERCENT, help="Doel SoC in % (default uit code)")
    parser.add_argument("--target-time", type=str, default=TARGET_TIME_HH_MM, help="Dagelijks doel tijd HH:MM (default uit code)")
    parser.add_argument("--rate", type=float, default=CHARGE_RATE_PCT_PER_HOUR, help="Laadsnelheid in %/uur voor planning")
    args, _ = parser.parse_known_args()
    VERBOSE = bool(args.verbose)
    state_file = args.state_file
    planning_enabled = not bool(args.no_plan)
    target_soc_cfg = float(args.target_soc)
    target_time_cfg = str(args.target_time)
    rate_cfg = float(args.rate)

    log("ZOE arrival poller gestart. Ctrl+C om te stoppen.")
    if VERBOSE:
        log("VERBOSE mode enabled.")

    # Load persisted snapshot
    persisted = load_state(state_file)
    last_soc = persisted.get("last_soc")
    last_soc_ts = persisted.get("last_soc_ts")
    last_km = persisted.get("last_km")
    last_km_ts = persisted.get("last_km_ts")
    plan = persisted.get("plan")
    if last_soc is not None and last_soc_ts:
        log(f"Laatste SoC bekend: {last_soc:.2f}% @ {last_soc_ts}")
    if last_km is not None and last_km_ts:
        log(f"Laatste km bekend: {last_km:.0f} km @ {last_km_ts}")
    if plan:
        log(
            "Hervat plan: doel {:.0f}% om {} (start om {}, resterend ~{:.2f} u bij rate {:.1f}%/h)".format(
                plan.get("target_soc", TARGET_SOC_PERCENT),
                plan.get("target_dt").strftime("%H:%M") if isinstance(plan.get("target_dt"), datetime) else "?",
                plan.get("start_at").strftime("%H:%M") if isinstance(plan.get("start_at"), datetime) else "?",
                plan.get("hours_needed", 0.0),
                rate_cfg,
            )
        )
        try:
            if float(plan.get("needed_pct", 0.0)) <= 0.05:
                log("Geen laden nodig: huidige SoC ≥ doel. AUTO_SHELLY doet niets.")
        except Exception:
            pass
        # If the target time has passed, roll the plan forward to the next window
        try:
            if planning_enabled and isinstance(plan.get("target_dt"), datetime) and plan["target_dt"] <= datetime.now():
                base_soc = last_soc if last_soc is not None else plan.get("measured_soc")
                if base_soc is not None:
                    plan = _compute_charge_plan(
                        current_soc=float(base_soc),
                        target_soc=target_soc_cfg,
                        target_time_str=target_time_cfg,
                        rate_pct_per_hour=rate_cfg,
                    )
                    log(
                        "Plan vernieuwd na herstart: SoC={:.2f}% → doel {:.0f}% om {} (start om {}, ~{:.2f} u).".format(
                            plan["measured_soc"],
                            plan["target_soc"],
                            plan["target_dt"].strftime("%H:%M"),
                            plan["start_at"].strftime("%H:%M"),
                            plan["hours_needed"],
                        )
                    )
                    save_state(state_file, {
                        "last_soc": last_soc,
                        "last_soc_ts": last_soc_ts,
                        "last_km": last_km,
                        "last_km_ts": last_km_ts,
                        "plan": plan,
                        "last_state": STATE_WAIT_DONGLE,
                    })
        except Exception:
            pass
    if not planning_enabled:
        log("Plannen uitgeschakeld (--no-plan). Er wordt geen nieuw plan aangemaakt en AUTO_SHELLY is uit.")

    # On restart, report Shelly state once (useful when car is connected, Shelly OFF)
    shelly_is_on = None
    if SHELLY_ENABLED:
        s0 = shelly_get_state()
        if s0 is not None:
            shelly_is_on = s0
            log(f"Shelly initial state: {'ON' if s0 else 'OFF'}")
            save_state(state_file, {
                "last_soc": last_soc,
                "last_soc_ts": last_soc_ts,
                "last_km": last_km,
                "last_km_ts": last_km_ts,
                "plan": plan,
                "last_state": STATE_WAIT_DONGLE,
                "last_shelly_state": shelly_is_on,
            })

    state = STATE_WAIT_DONGLE
    t_fast_start = None
    consecutive_soc_none = 0
    consecutive_odo_none = 0
    last_shelly_check = 0.0
    # keep last known Shelly state from above

    try:
        while True:
            now = time.time()

            if state == STATE_WAIT_DONGLE:
                if ping_host(ELM_HOST, timeout_s=1.0):
                    log("Ping OK — dongle is bereikbaar. Snel pollen voor eerste SoC/km...")
                    state = STATE_FAST_CAPTURE
                    t_fast_start = time.time()
                    consecutive_soc_none = 0
                    consecutive_odo_none = 0
                else:
                    time.sleep(PING_INTERVAL_IDLE)
                    continue

            elif state == STATE_FAST_CAPTURE:
                soc, km = try_poll_once()
                got_soc = soc is not None
                got_km = km is not None

                # Persist latest readings
                snap = {
                    "last_soc": soc if got_soc else last_soc,
                    "last_soc_ts": now_ts() if got_soc else last_soc_ts,
                    "last_km": km if got_km else last_km,
                    "last_km_ts": now_ts() if got_km else last_km_ts,
                    "plan": plan,
                    "last_state": state,
                }
                save_state(state_file, snap)
                last_soc = snap["last_soc"]; last_soc_ts = snap["last_soc_ts"]
                last_km = snap["last_km"]; last_km_ts = snap["last_km_ts"]

                # Plan as soon as we have a SoC
                if planning_enabled and got_soc and plan is None:
                    plan = _compute_charge_plan(
                        current_soc=soc,
                        target_soc=target_soc_cfg,
                        target_time_str=target_time_cfg,
                        rate_pct_per_hour=rate_cfg,
                    )
                    log(
                        "Laadplan: nu SoC={:.2f}%, doel {:.0f}% om {} → nodig ≈ {:.1f}% ({:.2f} u). Start om {}.".format(
                            plan["measured_soc"],
                            plan["target_soc"],
                            plan["target_dt"].strftime("%H:%M"),
                            plan["needed_pct"],
                            plan["hours_needed"],
                            plan["start_at"].strftime("%H:%M"),
                        )
                    )
                    if plan["needed_pct"] <= 0.05:
                        log("Geen laden nodig vandaag.")
                    # Persist plan
                    save_state(state_file, {
                        "last_soc": last_soc,
                        "last_soc_ts": last_soc_ts,
                        "last_km": last_km,
                        "last_km_ts": last_km_ts,
                        "plan": plan,
                        "last_state": state,
                    })

                if got_soc and got_km:
                    log("Eerste SoC + km binnen. Overschakelen naar langzame 5-minuten polling...")
                    state = STATE_SLOW_MONITOR
                    time.sleep(SLOW_POLL_INTERVAL)
                    continue

                # Handle fast window timeout
                if time.time() - t_fast_start >= FAST_POLL_MAX_WINDOW:
                    log("Snel-poll venster verlopen. Ga langzamer pollen zolang de dongle online is.")
                    state = STATE_SLOW_MONITOR
                    time.sleep(SLOW_POLL_INTERVAL)
                    continue

                # Keep trying fast
                time.sleep(FAST_POLL_INTERVAL)
                continue

            elif state == STATE_SLOW_MONITOR:
                # Check reachability
                if not ping_host(ELM_HOST, timeout_s=1.0):
                    log("Ping FAIL — dongle niet bereikbaar. Terug naar 30s ping.")
                    state = STATE_WAIT_DONGLE
                    # Persist state transition
                    save_state(state_file, {
                        "last_soc": last_soc,
                        "last_soc_ts": last_soc_ts,
                        "last_km": last_km,
                        "last_km_ts": last_km_ts,
                        "plan": plan,
                        "last_state": state,
                    })
                    time.sleep(PING_INTERVAL_IDLE)
                    continue

                # Optionally poll Shelly state
                if SHELLY_ENABLED and now - last_shelly_check >= SHELLY_POLL_INTERVAL:
                    s = shelly_get_state()
                    if s is not None and s != shelly_is_on:
                        shelly_is_on = s
                        log(f"Shelly charger is {'ON' if s else 'OFF'}.")
                        save_state(state_file, {
                            "last_soc": last_soc,
                            "last_soc_ts": last_soc_ts,
                            "last_km": last_km,
                            "last_km_ts": last_km_ts,
                            "plan": plan,
                            "last_state": state,
                            "last_shelly_state": shelly_is_on,
                        })
                    last_shelly_check = now

                # Auto operation (opt-in)
                if AUTO_SHELLY and planning_enabled and plan is not None and shelly_is_on is not None:
                    # Only if we actually need to charge
                    if plan.get("needed_pct", 0.0) > 0.05 and datetime.now() >= plan["start_at"] and not shelly_is_on:
                        log("Auto: starttijd bereikt → Shelly inschakelen.")
                        if shelly_set(True):
                            log("Shelly aan gezet.")
                            shelly_is_on = True
                        else:
                            log("Kon Shelly niet aanzetten.")

                # Poll once
                soc, km = try_poll_once()
                # Update persistence
                if soc is not None:
                    last_soc = soc; last_soc_ts = now_ts()
                if km is not None:
                    # Drive detection (log-only):
                    try:
                        if last_km is not None and (km - float(last_km)) >= 0.5:
                            log(f"Rijden gedetecteerd: +{km - float(last_km):.1f} km sinds laatste meting.")
                    except Exception:
                        pass
                    last_km = km; last_km_ts = now_ts()
                save_state(state_file, {
                    "last_soc": last_soc,
                    "last_soc_ts": last_soc_ts,
                    "last_km": last_km,
                    "last_km_ts": last_km_ts,
                    "plan": plan,
                    "last_state": state,
                    "last_shelly_state": shelly_is_on,
                })

                # Update plan if SoC changed
                if planning_enabled and plan is not None and soc is not None and abs(soc - plan["measured_soc"]) >= 0.2:
                    plan = _compute_charge_plan(
                        current_soc=soc,
                        target_soc=target_soc_cfg,
                        target_time_str=target_time_cfg,
                        rate_pct_per_hour=rate_cfg,
                    )
                    log(
                        "Plan geüpdatet: SoC={:.2f}% → doel {:.0f}% om {} (start om {}, ~{:.2f} u).".format(
                            plan["measured_soc"],
                            plan["target_soc"],
                            plan["target_dt"].strftime("%H:%M"),
                            plan["start_at"].strftime("%H:%M"),
                            plan["hours_needed"],
                        )
                    )
                    save_state(state_file, {
                        "last_soc": last_soc,
                        "last_soc_ts": last_soc_ts,
                        "last_km": last_km,
                        "last_km_ts": last_km_ts,
                        "plan": plan,
                        "last_state": state,
                        "last_shelly_state": shelly_is_on,
                    })

                time.sleep(SLOW_POLL_INTERVAL)
                continue

    except KeyboardInterrupt:
        log("Afsluiten op verzoek. Tot later!")

if __name__ == "__main__":
    main()
