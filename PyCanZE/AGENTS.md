# PyCanZE

PyCanZE is a Python spin-off of the CanZE project, an Android/iOS graphical
tool for Renault vehicles. The CSV data files from the original app are copied
here to support Python command-line tooling and experimentation.

The immediate aim is to poll selected vehicle registers and publish decoded
values over MQTT. A GUI similar to the original app may be built later.

## Current state

- Dataclasses and CSV parsers live in `models.py` and `parser.py`.
- A minimal UDS client in `uds.py` powers example utilities in `tools/` and
  `Testing/`.
- No MQTT interface or test suite is available yet.

Contributions are welcome as this module is under active development.


## Agent playbook: Codex analysis and porting plan

This repository includes both the original Android app sources and a Python UDS client. When running in a Codex (isolated) environment without live hardware, follow this plan to extract the app’s exact ELM/ISO‑TP behavior for LBC and port it to Python.

1) Locate Android ELM/ISO‑TP code paths
- Goal: find the init sequence (AT commands), header/filter handling, and multi‑frame (ISO‑TP) logic used for LBC 0x21 pages.
- Run these searches from repo root:
  - rg -n "AT(Z|E0|H0|S0|SP|AL|CAF|CFC1|FCSD|ST|SH|CRA|CF|CM)" app/src/main/java
  - rg -n "(7bb|79b|6103|6104|6107|\\b21_[0-9]{2}\\b|\"21[0-9A-Fa-f]{2}\")" app/src/main/java
  - rg -n "(IsoTp|FlowControl|filter|mask|ELM327|Dongle|Serial|Bluetooth|Wifi)" app/src/main/java
- Files of interest may include classes named like ELM327, Dongle, Transport, Protocol, and any LBC‑specific readers.

2) Document the app’s sequence
- Capture: order of AT commands; whether ATCAF is 0/1; use of ATCFC1/ATFCSD; use of ATCRA vs ATCF/ATCM; any ATST timeout; header settle delays; tester present cadence.
- Note per‑ECU handling for LBC (request 0x7BB, response 0x7B3/0x7C3/0x7F? and/or 0x7B? → 0x7C? depending on vehicle variant).

3) Port 1:1 to Python
- Update `pycanze/uds.py` to mirror the app’s flow exactly (bounded by ELM AT support):
  - Adopt same AT init and header/filter steps.
  - Match ISO‑TP timing (STmin, block size, collect windows) and session policy.
  - Keep non‑intrusive fallbacks toggleable via env flags.
- Validate basic EVC reads (SOC/SOH/HV) still pass.

4) Add a controlled fallback for LBC FF‑only cases
- Implement an optional “wide CF fallback”: temporarily enable ATH1 and open filter/mask to accept CFs, reassemble, then restore filters; guard with env `PYCANZE_WIDE_CF_FALLBACK=1` and a CLI flag in `battery_health.py`.
- Do not send manual flow control frames (ELM `ATCFC1` should handle FC); only widen reception.

5) Provide a sweep harness
- Use `PyCanZE/Testing/sweep_battery_health.sh` to run across CAF, mask, STmin, header settle, per‑ECU first‑0x21 delays, ATST, and ISO‑TP windows; logs go to `Testing/logs/battery_sweep_<ts>/`.

6) Deliverables in Codex PR
- Patch `uds.py` and `tools/battery_health.py` with the extracted behavior and the optional fallback flag.
- Include a short report in this file with: AT sequence, timing values, and any differences from current Python implementation.

Reference notes
- Python UDS currently supports: sessions (0x10 C0/F2/F3/81 best‑effort), tester present (0x3E), DID (0x22), local id (0x21), ATCFC1 and ATFCSD, ATSH/ATFCSH, ATCRA or ATCF/ATCM, header settle delay, per‑ECU first‑0x21 delay, and iso‑tp reassembly with retry.
- Known issue: some WiFi ELM327 clones drop CFs on LBC 0x21; timing/filtering is sensitive.


## ELM/ISO-TP findings (2025-08-30)

- Init sequence for the internal ELM327 driver:
  `ATE0; ATS0; ATH0; ATL0; ATAL; ATCAF0; ATFCSH77B; ATFCSD300000; ATFCSM1; ATSP6`
- Free-frame polling sets a temporary receive filter with `ATCRA`, runs `ATMA`, then flushes and optionally clears the filter with `ATAR`.
- ISO-TP requests clear any free-frame filter, select protocol (`ATSP7`/`ATSP6`), set header (`ATSH`), receive filter (`ATCRA`), and flow-control response (`ATFCSH`) before transmitting.
- Flow control uses `ATFCSM1` with `ATFCSD300000`, yielding block size `00` and STmin `00` (0 ms); no `ATST` command is issued【F:app/src/main/java/lu/fisch/canze/devices/ELM327.java†L181-L197】【5ce9be†L1-L2】, and the driver waits about 100 ms after cancelling `ATMA`【F:app/src/main/java/lu/fisch/canze/devices/ELM327.java†L520-L525】.
- Tester-present (`0x3E`) frames are scheduled every 1500 ms.
- Multi-frame transmissions send a first frame (`1…`) followed by numbered continuation frames (`2n…`); the receiver reassembles them and checks sequence numbers.
- Device reset levels map to `ATD` (soft) and `ATWS` (medium); `ATZ` is referenced conceptually for a hard reset but not issued.
- No usage of `ATCF` or `ATCM` commands was found.
- LBC request/response IDs vary by model: `0x7BB→0x79B` for legacy ZOE and Twingo 3 Ph2【F:app/src/main/assets/ZOE/_Ecus.csv†L5】【F:app/src/main/assets/Twingo_3_Ph2/_Ecus.csv†L7】, while ZOE Ph2 uses extended `0x18DAF1DB→0x18DADBF1`【F:app/src/main/assets/ZOE_Ph2/_Ecus.csv†L18】; LBC2 maps `0x7B6→0x796`【F:app/src/main/assets/ZOE/_Ecus.csv†L17】 or `0x18DAF1DC→0x18DADCF1`【F:app/src/main/assets/ZOE_Ph2/_Ecus.csv†L19】.

### Java source references for 1:1 porting

- **AT command order and flow-control setup** – the init array lists `ate0; ats0; ath0; atl0; atal; atcaf0; atfcsh77b; atfcsd300000; atfcsm1; atsp6`【F:app/src/main/java/lu/fisch/canze/devices/ELM327.java†L160-L202】
- **Free-frame filtering** – free-frame polls set `ATCRA` with the ECU’s response ID【F:app/src/main/java/lu/fisch/canze/devices/ELM327.java†L499-L508】
- **ISO‑TP per-request setup** – each request refreshes `ATSH`, `ATCRA`, and `ATFCSH`; protocol switches use `ATSP7/ATSP6`【F:app/src/main/java/lu/fisch/canze/devices/ELM327.java†L561-L595】
- **Header settle delay** – after cancelling `ATMA`, the driver flushes and waits before proceeding【F:app/src/main/java/lu/fisch/canze/devices/ELM327.java†L520-L526】
- **Tester-present cadence** – charging tech scheduling sends `BcbTesterAwake` every 1500 ms【F:app/src/main/java/lu/fisch/canze/activities/ChargingTechActivity.java†L80-L105】
- **LBC addressing variants** – assets show request/response IDs: `7BB→79B` for legacy models【F:app/src/main/assets/ZOE/_Ecus.csv†L5】, `7BB→79B` on Twingo Ph2【F:app/src/main/assets/Twingo_3_Ph2/_Ecus.csv†L7】, and extended `18DAF1DB→18DADBF1` for ZOE Ph2【F:app/src/main/assets/ZOE_Ph2/_Ecus.csv†L18】
- **Unused commands** – searches found no `ATCFC1`, `ATCF`, `ATCM`, or `ATST` usage (`rg -i atcfc1`, `atcf`, `atcm`, `atst`)【049216†L1-L2】【a0b7bc†L1-L2】【dcb514†L1-L2】【b87152†L1-L2】
