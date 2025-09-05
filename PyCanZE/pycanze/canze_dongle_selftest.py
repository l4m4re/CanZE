#!/usr/bin/env python3
# canze_dongle_selftest.py (fixed parser for glued hex)
# Voert het CanZE "Dongle test script" uit en checkt tolerant op antwoorden.

import socket, time, re, sys

ELM_HOST = "192.168.2.21"   # <— zet IP van je dongle
ELM_PORT = 35000            # <— en poort
TIMEOUT_S = 3.0
SLEEP = 0.10
VERBOSE = False

G = "\033[92m"; R = "\033[91m"; Y = "\033[93m"; N = "\033[0m"

HEX2 = re.compile(r"[0-9A-Fa-f]{2}")  # GEEN woordgrenzen meer

def send(sock, cmd, sleep=SLEEP):
    if VERBOSE: print(">>>", cmd)
    sock.sendall((cmd + "\r").encode("ascii"))
    time.sleep(sleep)

def read_until_prompt(sock):
    sock.settimeout(TIMEOUT_S)
    buf = b""
    while True:
        try:
            chunk = sock.recv(4096)
        except socket.timeout:
            break
        if not chunk:
            break
        buf += chunk
        if b">" in buf:
            break
    txt = buf.decode(errors="ignore")
    if VERBOSE: print(f"[RAW RECV] {repr(txt)}")
    lines = [l.strip() for l in txt.replace("\r","\n").split("\n")]
    lines = [l for l in lines if l and l != ">"]
    if VERBOSE and lines:
        print("\n".join(lines))
    return lines

def expect_reset(sock):
    send(sock, "ATZ", sleep=0.3)
    lines = read_until_prompt(sock)
    txt = "\n".join(lines).upper()
    ok = ("ELM" in txt) or any("OK" in l.upper() for l in lines)
    print(f"{'ATZ (reset)':<28} {'OK' if ok else 'FAIL'}")
    if VERBOSE and lines: print("\n".join(lines))
    return ok

def expect_ok(sock, cmd, label):
    send(sock, cmd); lines = read_until_prompt(sock)
    ok = any("OK" in l.upper() for l in lines)
    print(f"{label:<28} {'OK' if ok else 'FAIL'}")
    if not ok and VERBOSE: print("\n".join(lines))
    return ok

def parse_all_bytes(lines):
    """
    Haal ALLE hex bytes (ook als ze aan elkaar geplakt zijn, bv '0662200600B5FBAA').
    Filter 'NO DATA', 'ERROR', etc. eruit.
    """
    bs = []
    for ln in lines:
        up = ln.upper()
        if any(k in up for k in ["NO DATA","ERROR","SEARCHING","BUS INIT"]):
            continue
        # verwijder niet-hex tekens, dan per 2 chars splitten
        only_hex = "".join(ch for ch in ln if ch.upper() in "0123456789ABCDEF")
        # als er spaties stonden pakt de regex die ook; dit maakt 't uniform
        pairs = HEX2.findall(only_hex)
        bs += [p.upper() for p in pairs]
    return bs

def expect_udstest(sock):
    # CanZE: stuur 03222006 en verwacht iets dat (effectief) "62 20 06 ..." bevat
    send(sock, "03222006")
    lines = read_until_prompt(sock)
    if VERBOSE: print("\n".join(lines))
    bs = parse_all_bytes(lines)
    ok = False
    odo_info = None
    for i in range(len(bs)-2):
        if bs[i:i+3] == ["62","20","06"]:
            ok = True
            payload = bs[i+3:]
            # Decodeer mogelijke kilometerwaarden uit 3 of 4 bytes (big-endian)
            def to_int(bl):
                try:
                    return int("".join(bl), 16)
                except Exception:
                    return None
            raw3 = to_int(payload[:3]) if len(payload) >= 3 else None
            raw4 = to_int(payload[:4]) if len(payload) >= 4 else None
            candidates = []
            if raw3 is not None:
                candidates.append(("3B", raw3, raw3/10.0))
            if raw4 is not None:
                candidates.append(("4B", raw4, raw4/10.0))
            odo_info = (payload, candidates)
            break
    print(f"{'03222006 → 622006…':<28} {'OK' if ok else 'FAIL'}")
    if ok and odo_info:
        payload, candidates = odo_info
        print(f"{'UDS 0x2006 (raw)':<28} {' '.join(payload) if payload else '-'}")
        # Kies een leesbare presentatie, toon beide schalen
        for tag, val, val01 in candidates:
            print(f"{'Odometer '+tag:<28} {val} km  (alt: {val01:.1f} km)")
    else:
        if not lines:
            print(f"{Y}Hint:{N} geen antwoord ontvangen — is de auto/lader wel actief?")
        else:
            raw = " | ".join(lines)
            print(f"{Y}Ontvangen:{N} {raw}")
    return ok

def expect_soc(sock):
    send(sock, "03222002")
    lines = read_until_prompt(sock)
    bs = parse_all_bytes(lines)
    ok = any(bs[i:i+3] == ["62","20","02"] for i in range(len(bs)-2))
    if ok:
        # simpele decode (2 bytes na 62 20 02)
        for i in range(len(bs)-4):
            if bs[i:i+3] == ["62","20","02"]:
                if i+5 < len(bs):
                    b0 = int(bs[i+3],16); b1 = int(bs[i+4],16)
                    raw = (b0<<8)|b1
                    soc = (raw*2)/100.0
                    print(f"{'03222002 (SoC) → 622002…':<28} OK  (SoC≈{soc:.2f}%)")
                    return True
    print(f"{'03222002 (SoC) → 622002…':<28} FAIL")
    if lines: print("Ontvangen:", " | ".join(lines))
    return False

def monitor_can(sock, seconds=3):
    # 11-bit filter op 0x699, Monitor All, daarna stoppen
    send(sock, "ATCRA 699"); read_until_prompt(sock)
    send(sock, "ATMA")
    t_end = time.time() + seconds
    seen = 0
    while time.time() < t_end:
        try:
            sock.settimeout(1.0)
            chunk = sock.recv(4096)
            if not chunk: break
            txt = chunk.decode(errors="ignore")
            for ln in [l.strip() for l in txt.replace("\r","\n").split("\n") if l.strip()]:
                if ln == ">": continue
                if VERBOSE: print(ln)
                seen += 1
        except socket.timeout:
            pass
    send(sock, "ATAR"); read_until_prompt(sock)
    # filter uit
    send(sock, "ATCRA 000"); read_until_prompt(sock)
    ok = seen > 0
    print(f"{'ATCRA699 + ATMA (stop ATAR)':<28} {'OK' if ok else 'FAIL'}")
    if not ok:
        print(f"{Y}Hint:{N} geen CAN-monitorregels gezien. Probeer met de auto aan/ladend en nog eens.")
    return ok

def main():
    print("=== CanZE dongle selftest ===")
    print("Zorg dat de ZOE **wakker** is (Ready of ladend) voor stap 3.\n")
    try:
        with socket.create_connection((ELM_HOST, ELM_PORT), timeout=TIMEOUT_S) as s:
            # Stap 1: basis setup
            print("[Stap 1] Basis AT-setup (verwacht overal OK)")
            ok = True
            ok &= expect_reset(s)
            ok &= expect_ok(s, "ATE0",  "ATE0 (echo off)")
            ok &= expect_ok(s, "ATS0",  "ATS0 (no spaces)")
            ok &= expect_ok(s, "ATSP6", "ATSP6 (ISO15765-4 CAN)")
            ok &= expect_ok(s, "ATAT1", "ATAT1 (adaptive timing)")
            ok &= expect_ok(s, "ATCAF0","ATCAF0 (autoformat off)")

            # Stap 2: headers
            print("\n[Stap 2] Headers instellen")
            ok &= expect_ok(s, "ATSH7E4",   "ATSH7E4 (request hdr)")
            ok &= expect_ok(s, "ATFCSH7E4", "ATFCSH7E4 (FC header)")

            # Stap 3: UDS proef
            print("\n[Stap 3] UDS proef (DID 0x2006)")
            uds = expect_udstest(s)

            print("\nExtra: SoC opvragen (DID 0x2002)")
            soc = expect_soc(s)

            # Stap 4: monitor
            print("\n[Stap 4] CAN-monitor")
            mon = monitor_can(s, seconds=3)

            print("\nResultaat:")
            if uds and mon:
                print(f"{G}OK{N} — Dongle lijkt geschikt voor CanZE/UDS.")
            elif mon and not uds:
                print(f"{Y}De CAN-monitor werkt, maar UDS-read op 0x2006 faalt.{N} "
                      "Dit kan komen door slaapstand of ECU-variant. Test in Ready en tijdens laden.")
            else:
                print(f"{R}FAIL{N} — Dongle is waarschijnlijk ongeschikt of auto is niet wakker.")
    except Exception as e:
        print(f"{R}Fout:{N} {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
