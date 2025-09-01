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

## Handling vehicle states and sentinel values (2025-09-01)

When agents/pollers consume PyCanZE, decide what to read/publish based on vehicle state. Some EVC/LBC values are unavailable or placeholders while the car sleeps, especially with the charger plugged but inactive.

- States to detect: ready/driving, charging, charger-connected-sleep, parked-sleep.
- Simple indicators:
  - 7ec.24.622002 SOC HV battery — often 0.0% in charger-connected-sleep.
  - 7ec.24.623319 Charger pump speed — 0% asleep; >0% charging/cooling.
  - 7ec.24.623028 DCDC Load — 0% asleep; small >0% when charging.
  - 7ec.31.6233cd ($33CD) Request of Hvac power Relay -> appears to differ between sleep and charge connected sleep.
  - 7ec.25.623328 ($3328) Heat pump Request -> appears to be zero in charge connected sleep mode.
  - 7ec.24.6234ad ($34AD) Set-point for the charge current for the JB2 -> seems to be >0 when charging
  - 7ec.30.6234dd ($34DD) Request for PEB Charge mode V2 -> seems to be 2.0 when charging -> it’s an enum with these values:
            0: Unavailable value
            1: No charge requested
            2: Charge requested
            3: Not used
  - 7ec.29.6233ea ($33EA) CAN signal for the status of the plugs connection 
            0: No plug connected
            2: Plug connected — no button pressed
            4: 1 plug connected — button pressed
            6: 2 plugs connected
            7: Unavailable value

Guidance per state:
- Charger-connected-sleep: skip publishing these (treat as unavailable):
  - 7ec.24.623203 HV LBC voltage measure (shows 500.0 V placeholder)
  - 7ec.24.623204 HV LBC current measure (shows ~−6144 A placeholder)
  - 7ec.24.623206 SOH HV battery (can exceed 100%)
  - 7ec.24.623451 Estimated range (may report max like 1023 km)



Notes:
- We intentionally don’t filter these inside the decoder; handle in your agent based on state.
- 7ec.24.622002 = 0.0% is a strong signal of charger-connected-sleep.
- LBC current during charging: logs showed ~−6143 A, which is unrealistic. This likely points to a scaling/offset mismatch for 623204 on some variants. Prefer EVC-specific overrides; if still wrong, review the CSV definitions for 623204 for your vehicle variant.

Update (2025-09-01): Adjusted ZOE/EVC_Fields.csv for 7ec.24.623204 to use the generic scaling (resolution .25, offset 32768, decimals 1) to avoid the −6144 A artifact observed during charging on some cars. If your variant still reports implausible values, consider sourcing HV current from an alternative DID (e.g., $3110 Charge current measure or $3042 HV INV current) in your agent.

## Java log replayer

The `Testing/LogReplayer` directory provides a small Java utility to turn raw ELM327 dumps into decoded JSON. No compiled classes are checked in; rebuild as needed:

```bash
javac -d PyCanZE/Testing/LogReplayer PyCanZE/Testing/LogReplayer/LogReplayer.java
java -cp PyCanZE/Testing/LogReplayer lu.fisch.canze.tools.LogReplayer <input.raw> <output.json>
```


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

## Roadmap and next goals

Primary goal: simple, reliable Home Assistant integration for monitoring and charging planning, keeping SoC between roughly 20–30% and 70–80%.

Near‑term deliverables
- MQTT poller (every ~5 minutes): publish a compact snapshot with metrics we already read reliably via EVC.
  - Suggested baseline fields (proven today):
    - SoC (%) — EVC 0x22/0x2002
    - SOH (%) — EVC 0x22/0x3206
    - HV voltage (V) — EVC 0x22/0x2004 or 0x3008
    - Odometer (km) — EVC 0x22/0x2006
  - Optional as we confirm: charging status/plug state (EVC/UCH), charge power (kW), AC voltage/current (PEB), etc.
- Home Assistant wiring:
  - Option A (manual): subscribe HA to a single state topic (e.g., `canze/zoe/state`) and template sensors in HA YAML.
  - Option B (MQTT Discovery): publish discovery configs under `homeassistant/sensor/zoe_*` so sensors appear automatically.
- Battery detail snapshot (less frequent, e.g., every 30–60 minutes or on‑demand):
  - LBC 21_03: min/max cell voltage, OCV
  - LBC 21_04: min/avg/max battery temperature
  - LBC 21_07: balancing flags summary
  - Publish to a separate topic (e.g., `canze/zoe/diag`) to avoid flooding HA history; optionally disabled by default.

Suggested MQTT schema
- State topic: `canze/zoe/state`
  - Payload:
    - `{ "ts":"ISO8601", "soc_pct":float, "soh_pct":float, "hv_v":float, "odometer_km":float }`
- Diagnostic topic (optional): `canze/zoe/diag`
  - Payload:
    - `{ "ts":"ISO8601", "lbc": { "v_min":float, "v_max":float, "ocv":float, "t_min":float, "t_avg":float, "t_max":float, "bal_1":int, "bal_2":int, "bal_3":int } }`

Update cadence
- Frequent snapshot (state): every 5 minutes (configurable), with a one‑shot fast capture when the dongle first comes online.
- Diagnostic snapshot: 30–60 minutes when the car is awake, or on command.

Implementation notes
- Reuse `Testing/zoe_arrival_poller.py` structure for connectivity/pacing; extract the read logic into a shared helper.
- Add `tools/mqtt_poller.py`:
  - CLI: `--host`, `--port`, `--interval`, `--mqtt-url`, `--mqtt-user`, `--mqtt-pass`, `--ha-discovery`, `--topic-prefix`.
  - Publishes JSON as above; optional HA discovery configs.
- LBC detail reads remain behind a flag until the ISO‑TP reliability work (Codex alignment + optional wide‑CF fallback) is merged.


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

## Vehicle states and OBD reachability (2025-08-31)

Field observation with a home EVSE controlled by a Shelly (arrival poller `--always-fast`): when the EVSE is switched OFF while the plug remains inserted, the vehicle transitions to a distinct sleep mode after roughly one minute. During this transition, EVC DIDs continue to answer briefly before going silent.

States we currently distinguish operationally:

1) offline — Wi‑Fi dongle unreachable (out of range or powered off).
2) ready — Vehicle just arrived/ignition cycle. EVC responds reliably; other ECUs as usual. Good window to read.
3) sleep — Vehicle fully asleep; most UDS requests return no data.
4) charger connected sleep — EVSE plugged, Shelly OFF. The car detects a charger but has no active pilot/charging. Empirically, EVC (e.g., SOC $2002, Odometer $2006, SOH $3206) keeps replying for ~50–60 seconds after power‑off, then transitions to no data. We observed one Odometer “no data” blip during the transition before it stabilized to no data.
5) charging — EVSE ON. Vehicle wakes sufficiently for polling; behavior appears similar to “ready” for EVC reads. Differences vs “ready” for other ECUs TBD.

Implications for tools
- Arrival poller: Expect SoC/SOH/Odo to be available for about a minute after switching the EVSE OFF, then transition to no data while the dongle remains pingable. For testing or to catch that last minute, use `--always-fast` so we do not miss the window.
- Scanner: Continue to skip ECUs that report CAN_ERROR or NO DATA and proceed (implemented), which is normal in sleep states.
- Planning: Don’t rely on the car staying awake when the EVSE is OFF but plugged; schedule reads accordingly or re‑enable the EVSE briefly if a fresh snapshot is required.

### Java source references for 1:1 porting

- **AT command order and flow-control setup** – the init array lists `ate0; ats0; ath0; atl0; atal; atcaf0; atfcsh77b; atfcsd300000; atfcsm1; atsp6`【F:app/src/main/java/lu/fisch/canze/devices/ELM327.java†L160-L202】
- **Free-frame filtering** – free-frame polls set `ATCRA` with the ECU’s response ID【F:app/src/main/java/lu/fisch/canze/devices/ELM327.java†L499-L508】
- **ISO‑TP per-request setup** – each request refreshes `ATSH`, `ATCRA`, and `ATFCSH`; protocol switches use `ATSP7/ATSP6`【F:app/src/main/java/lu/fisch/canze/devices/ELM327.java†L561-L595】
- **Header settle delay** – after cancelling `ATMA`, the driver flushes and waits before proceeding【F:app/src/main/java/lu/fisch/canze/devices/ELM327.java†L520-L526】
- **Tester-present cadence** – charging tech scheduling sends `BcbTesterAwake` every 1500 ms【F:app/src/main/java/lu/fisch/canze/activities/ChargingTechActivity.java†L80-L105】
- **LBC addressing variants** – assets show request/response IDs: `7BB→79B` for legacy models【F:app/src/main/assets/ZOE/_Ecus.csv†L5】, `7BB→79B` on Twingo Ph2【F:app/src/main/assets/Twingo_3_Ph2/_Ecus.csv†L7】, and extended `18DAF1DB→18DADBF1` for ZOE Ph2【F:app/src/main/assets/ZOE_Ph2/_Ecus.csv†L18】
- **Unused commands** – searches found no `ATCFC1`, `ATCF`, `ATCM`, or `ATST` usage (`rg -i atcfc1`, `atcf`, `atcm`, `atst`)【049216†L1-L2】【a0b7bc†L1-L2】【dcb514†L1-L2】【b87152†L1-L2】

## AT port report (2025-02-14)

- **AT init sequence** – `ATZ; ATE0; ATS0; ATH0; ATL0; ATAL; ATCAF{0|1}; ATFCSH77B; ATFCSD3000xx; ATFCSM1; ATSP6`
- **Timing defaults** – header settle 0 ms; first‑0x21 delay 0 ms (configurable); TesterPresent every 1500 ms; ISO‑TP collect window 2.5 s with 1.2 s CF read timeout.
- **Python differences** – optional wide‑CF fallback widens filters and enables `ATH1` when CFs are missing; flow control retry reasserts `ATCFC1`/`ATFCSD` before one retry; environment knobs (`PYCANZE_*`) expose the above timings.


## Java vs Python parity report (2025-08-30)

Summary: We’re very close for UDS over ISO‑TP on 11‑bit CAN. AT init, header/filter handling, and ISO‑TP RX logic align with the app. We intentionally added extra robustness (sessions, TesterPresent, FC reassert, optional wide‑CF fallback). Missing by design: free‑frame capture and 29‑bit addressing.

- AT initialization
  - Java: `ATE0; ATS0; ATH0; ATL0; ATAL; ATCAF0; ATFCSH77B; ATFCSD300000; ATFCSM1; ATSP6`
  - Python: same order; CAF and STmin are tunable; optional `ATST` supported.
- Header/filter management (ISO‑TP)
  - Java: per‑request `ATSH <to>`, `ATCRA <from>`, `ATFCSH <to>`; caches last ID; switches 11/29‑bit via `ATSP6/7` and `ATCP`.
  - Python: per‑field `ATSH <req>`, `ATCRA <resp>` or `ATCF/ATCM` (toggle); `ATFCSH <req>`; caches current req; 11‑bit only.
- ISO‑TP transmit
  - Java: builds FRST/NEXT for long payloads.
  - Python: only short requests (sufficient for 0x21/0x22). No long‑TX yet.
- ISO‑TP receive
  - Java: parses Single/First; reads expected CF count; checks SN; flushes to `>`.
  - Python: parses FF; collects CFs with sequence checks; adds FC reassert retry and optional wide‑CF fallback; configurable timeouts.
- Free‑frame capture
  - Java: `ATCRA` + `ATMA`, then cancel with `x` and flush; optional `ATAR`.
  - Python: not implemented (UDS focus).
- Recovery/flush
  - Java: `killCurrentOperation()` uses `x`, flush, `x\r` to provoke `?` and clear state.
  - Python: simple read‑until‑`>`; no explicit kill routine yet.
- 29‑bit addressing
  - Java: `ATSP7` + `ATCP` when needed.
  - Python: 11‑bit only for now.
- Sessions/keep‑alive
  - Java ELM driver: sessions handled elsewhere in app.
  - Python: best‑effort `0x10` sessions and periodic `0x3E` TesterPresent built‑in.

Gaps to close (optional, low‑risk):
- Add an `atma` helper (free‑frame capture) mirroring Java’s `ATCRA` → `ATMA` → cancel/flush sequence; restore filters before ISO‑TP.
- Add a `kill()` utility that mimics `killCurrentOperation()` (`x`, timed flush, `x\r`, flush until `?` then `>`), gated behind a retry policy.
- Guarded 29‑bit mode: detect 29‑bit ECUs in the DB and switch via `ATSP7` + `ATCP` (feature‑flagged, default off).

What we intentionally keep as enhancements vs app:
- Flow‑control reassert retry and wide‑CF fallback for LBC FF‑only clones.
- Exposed tunables (`PYCANZE_*`) for CAF, STmin, header settle, first‑0x21 delay, ISO‑TP windows, and mask filtering.


## Field coverage snapshot (2025-08-30)

Source: `tools/zoef_ready_30-08.log` and `tools/zoef_bat-health_30-08.log` (legacy ZOE, 11‑bit).

- EVC (7E4→7EC): 1077/1112 fields returned values; multi‑frame and single‑frame reads are stable.
  - Examples observed:
    - SOC ($2002): 71.12–71.14%
    - HV voltage ($2004): ~370.5–371.5 V
    - 12V voltage ($2005): ~13.2 V
    - Odometer ($2006): 46845 km
    - Engine/drive status ($2010): 0 (stopped)
    - Various identification DIDs (6180/61F0/61FF) decoded
- LBC (7BB→79B): Service 0x21 pages read successfully (multi‑frame confirmed)
  - 21_03 OCV: parsed (example 3.86 V)
  - 21_04 temperatures: multi‑frame received; several bytes were 0xFF placeholders; average/min/max decoded but scaling needs verification (295°C clearly wrong → unit/scaling to be fixed)
  - 21_07 balancing status: three banks parsed (values looked like raw bitmasks 0, 2, 128 → needs bit decoding)
- LBC2: 8/8 identification values (e.g., ManufacturerIdentificationCode = 2) available.
- USM: 575/608 values reported present; details not yet curated.
- Parking‑Sonar: 257/312 values reported present; details not yet curated.
- Other ECUs (BCB‑OBC, DCM, EPS, HVAC, PEB, TDB, UCH): largely `None` in this run, likely session/timing/decoder gaps or not applicable when the car is ready/idle.

Notes and inconsistencies to fix:
- LBC page decoders: several fields show unrealistic values (e.g., cell V min/max and temperatures). Recheck bit ranges and scaling in `ZOE/_Fields.csv` and adjust parsing.
- 0xFF‑filled segments: treat as “not available” when present within 21_04 blocks.
- Balancing flags: interpret 21_07 bytes as bitfields and expose per‑group ON/OFF booleans.


## Priority metrics for Home Assistant and diagnostics

Goal A — Charging planning and monitoring (low‑frequency snapshot, ~5 min):
- SOC (EVC $2002)
- HV battery voltage (EVC $2004)
- Charge state / engine status (EVC $2010)
- Plug/charging active flags (EVC/UCH, to be confirmed from DB)
- Charge power and AC line values (PEB/BCB‑OBC: power, AC voltage/current) — optional where reliable
- Battery temperature (mean) — optional from LBC 21_04 once scaling validated
- Odometer (EVC $2006) — optional context

Goal B — Battery health monitoring (less frequent, e.g., 30–60 min or on‑demand):
- SOH (EVC $3206)
- OCV snapshot (LBC 21_03)
- Cell voltage min/max (LBC 21_03) — after decoder calibration
- Battery temperature min/avg/max (LBC 21_04) — after handling 0xFF padding and scaling
- Balancing status (LBC 21_07, groups 1–3) — expose as bitmask/booleans
- Optional: charging history counters if stable (EVC/BCB)

Balancing guidance (operational):
- Passive balancer in LBC engages near the top of the SOC window (>95–99%).
- Daily use: stay ~20–80% for longevity. Periodically (e.g., monthly) charge to 100% and keep plugged for a few hours to allow balancing.
- HA idea: automation to remind or schedule a “balancing‑charge” monthly when battery temperature and schedule permit.


## SOH estimation beyond ECU value (2025-08-30)

Question: OBD reports SOH ~90%, while a commercial tool estimated ~92.1%. Can we estimate SOH more accurately using richer data?

Short answer: Yes, we can produce an independent SOH estimate that may be closer to instantaneous “true” usable capacity under known conditions. The ECU’s SOH is a long‑term, temperature‑compensated internal metric; external estimates can differ depending on normalization and measurement windows.

Approaches
- Capacity‑based (preferred)
  - Idea: compute usable capacity from energy or charge transfer over a SOC window under controlled conditions.
  - Needs: pack HV voltage, HV current or DC power, SOC, battery temperature (and preferably ambient), time.
  - Method: during a steady charge (e.g., AC L2) or steady discharge (gentle cruise), integrate DC power over Δt to get ΔE, or integrate current to get ΔAh over a SOC window (e.g., 20→80%). UsableCapacity ≈ ΔE / (ΔSOC). SOH_cap = UsableCapacity / NominalCapacity_new.
  - Normalize: correct to a reference temperature (e.g., 25 °C) and mid‑SOC; discard segments with strong dynamics.
- Resistance‑based
  - Idea: internal resistance grows with aging. Estimate R = ΔV/ΔI from current steps and compare to a reference map vs SOC, temperature.
  - Needs: fast samples of HV voltage, current, SOC, temperature during load/regen steps.
  - Outputs a health indicator correlated to SOH; useful as a cross‑check rather than a standalone SOH.
- OCV‑based (rest)
  - Idea: use per‑cell open‑circuit voltage at rest to place the pack on the OCV‑SOC curve; track capacity shift/plateau deformation.
  - Needs: per‑cell voltages (LBC 21_03) after rest, SOC, temperature. Multiple snapshots across SOC improve accuracy.
  - More complex; good for diagnostics and imbalance detection.
- Balance/dispersion indicators
  - Track min/max/σ of cell voltages at rest; monitor 21_07 balancing flags. Not SOH per se, but informs when to schedule a balancing charge.

Signals we have/need
- Have (stable today):
  - SOC (EVC $2002), HV voltage (EVC $2004), SOH (EVC $3206), LBC: per‑cell voltages (21_03), battery temps (21_04), balancing flags (21_07).
- Need for capacity/IR estimates:
  - HV current or DC power (from EVC/PEB; if unavailable, approximate from AC side with efficiency assumption or external meter).
  - Battery/ambient temperature (LBC 21_04 provides pack temps; ambient can be approximated or read if available).
  - Nominal (new) capacity per variant (config‑driven; avoid hard‑coding).

Procedure (capacity‑based, charge window example)
1) Preconditions: pack temperature in a moderate range (e.g., 15–30 °C), car awake, no thermal runaways.
2) Log at ~1 Hz: ts, SOC, HV_V, HV_I or DC power, pack temps, min/max cell V.
3) During a steady AC charge between e.g., 20→80% SOC, integrate DC energy (∑ P_dc·Δt) or charge (∑ I·Δt) within quality gates (reject spikes; clamp to SOC range).
4) Compute usable capacity: Ĉ = ΔE / (ΔSOC) (kWh) or Âĥ = ΔAh / (ΔSOC) (Ah). Convert between Ah/kWh using mean pack voltage within window.
5) Normalize Ĉ to reference temperature using a simple correction curve (placeholder until calibrated); report SOH_cap = Ĉ / C_nominal.
6) Compare to ECU SOH; report both and a confidence flag (window length, temperature, current stability).

Implementation plan
- Add `tools/soh_estimator.py` to log required signals and compute SOH_cap with quality gates and temperature normalization.
- Use per‑model nominal capacity from a small config file (e.g., 22 kWh, 41 kWh; editable).
- Add an optional IR estimator: detect current steps from drive logs and compute R_dc(SOC,T) trends.
- Publish SOH_est and trends via MQTT; keep monthly history. If divergence >~2 pp vs ECU SOH, flag for review.

Limitations
- Accuracy depends on availability and fidelity of DC current/power; AC‑side proxies require efficiency assumptions.
- SOC meters, temperature effects, and recent balancing state introduce bias; rest periods improve OCV‑based checks.
- ECU SOH remains authoritative for warranty; our estimate is complementary for monitoring and planning.


## Practical logging strategy (SOC monitoring and SOH estimation)

Context: Nightly charging on a “granny” EVSE measured by a Shelly (AC power/energy). Vehicle data via EVC/LBC. Some LBC temperature decoders are currently suspect; treat them as TBD.

Objectives
- SOC monitoring (for HA charge planning/notifications)
- SOH estimation over time using charge sessions (capacity‑based)

Signals to log
- From Shelly (AC side): timestamp, power (W), energy total (Wh), voltage (V), current (A), device temp (optional)
- From car (every 5–10 s is sufficient overnight):
  - EVC: SOC ($2002), HV voltage ($2004), engine/charge status ($2010), optional charge state/plug flags
  - EVC: inverter or environment proxy temperature (e.g., $3047) for context
  - LBC (optional now; decoder fix pending): pack temperatures (21_04), balancing flags (21_07), cell voltages (21_03)
  - Odometer ($2006) once per session for records

Sampling cadence
- Baseline: 5‑minute logging is sufficient for HA planning and capacity estimation at ~13 A (≈6.15% SOC/hour → ~0.51% SOC per 5 min).
- Increase temporarily to 30–60 s around session start/stop and above 95% SOC (balancing phase) to catch transitions cleanly.
- If performing resistance/step analysis while driving, use ≤1 s where feasible; otherwise keep the 5‑minute cadence.

SOC monitoring pipeline
- Log SOC, charge status, and Shelly power to CSV/JSON at 5–10 s cadence during charging windows.
- Derive: charge energy (from Shelly ΔWh), estimated DC energy (apply efficiency curve), time‑to‑target SOC, and simple alerts (plugged but not charging; reached target; monthly “balancing‑charge” reminder).

SOH estimation (capacity‑based) per session
- Choose a window within a single steady AC charge, e.g., SOC 20→80% (or widest sub‑window available that avoids >95%).
- Compute AC energy from Shelly: ΔE_ac = EnergyEnd − EnergyStart.
- Convert to DC: ΔE_dc = η(P_ac, T) · ΔE_ac, where η is an efficiency factor (start with 0.88–0.93; calibrate vs EVC HVV·I if available).
- Compute usable capacity estimate: Ĉ = ΔE_dc / (ΔSOC).
- Normalize to reference temperature (e.g., 25 °C) with a simple linear correction until we have a better map.
- Store per‑session SOH_cap = Ĉ / C_nominal alongside ECU SOH and a confidence score (window size, temperature band, stability).

Quality gates and stability checks
- Exclude top region SOC >95% (balancing zone) and very low SOC where heater/pumps may distort efficiency.
- Require minimum window ΔSOC ≥ 30 pp and duration ≥ 30 min for a “good” estimate.
- Discard segments where Shelly power varies >15% within short intervals (unstable supply) or where charge pauses.
- Temperature band: prefer 15–30 °C; record temperature proxy used (EVC $3047 for now).

Calibration and improvements
- If DC current/power becomes available from EVC/PEB, switch ΔE_dc integration to on‑pack values and use Shelly data only as a cross‑check.
- Fit η(P_ac, T) using a few full sessions to reduce bias from the AC→DC conversion.
- Fix LBC 21_04 decoder and then incorporate pack mean temperature instead of proxy.

Deliverables
- `tools/soh_logger.py`: merges Shelly MQTT/REST polls with EVC reads into a unified CSV and computes per‑session SOH_cap; publishes to MQTT (optional).
- Config file with nominal capacity per variant and an initial η default; adjustable via CLI.
- HA sensors: SOC, charge power, charge energy, estimated DC energy, ECU SOH, estimated SOH, confidence, next balancing reminder.


## Charging control strategy (staged)

Goal: Reach a user target SOC by a set wake time without stressing hardware. Prefer graceful control (pilot/API) over hard AC cuts.

Stage 1 — Schedule start, manual stop, rare emergency cutoff
- Compute start time so that SOC at wake is within ~±5% of target.
  - Inputs: current SOC (EVC $2002), AC current (setpoint), AC voltage (Shelly), efficiency η, taper profile near top.
  - Heuristic: assume a linear SOC gain at the current setpoint below ~85% SOC; add a safety buffer for taper (e.g., +20–30 min).
- Turn EVSE on at zero load only (Shelly on just before planned start); avoid switching under load.
- Stop charging manually in the morning to prevent relay arcing.
- Emergency cutoff (rare): if SOC drifts high (e.g., ≥ 90%), allow Shelly to open once to stop charge.
  - Add hysteresis and a cooldown to avoid flapping.
  - Monitor Shelly temperature; log events; treat as exception, not daily routine.

Stage 2 — HA automation for start scheduling
- Add an HA automation that:
  - Polls SOC every 5 min; estimates time-to-target using recent charge slope or a configured %/h map per setpoint.
  - Schedules Shelly ON so predicted SOC at wake≈target; shifts earlier if cold temps reduce efficiency.
  - Keeps Shelly OFF until start to ensure zero-load switching.
  - Optional: if the EVSE exposes an API/OCPP, prefer pause/disable over AC cut for mid-session control.

Stage 3 — Dash “Stop charge” button integration (future)
- If the dash stop-charge is a simple mechanical momentary switch, bridge its two pads with an isolated, normally-open contact:
  - Reed relay or PhotoMOS (bidirectional dry contact) across the button pads; 100–300 ms pulse to simulate a press.
  - Drive the relay/PhotoMOS from an ESP32/ESPHome; isolate grounds; power via fused buck converter from an accessory circuit.
  - Only press when charging is active and SOC ≥ target; enforce a minimum interval between presses.
- Validate that pressing works when the car is locked; if not, defer to EVSE-side control.
- Alternatives: a “button pusher” (servo/SwitchBot) or using a spare key-fob button with an opto-isolated press driver.

Out of scope / not used
- OBD/UDS write to stop charging: not supported safely (security access, undocumented). We keep the OBD path read-only.
- RF record/replay of key-fob: rolling codes; not viable and a security risk.

Operational notes
- Monthly balancing: schedule an occasional 100% charge and hold for a few hours to allow LBC balancing; avoid doing this frequently.
- Protect switching gear: If cutting AC is required more often, use the Shelly only to drive a proper DIN contactor (≥25–40 A AC‑7a), or use an SSR with heatsink; still prefer pilot/API pause.
- Safety: Add hysteresis and cooldowns for any automatic stop; ensure wiring gauge/enclosure are adequate; avoid frequent high‑load cutoffs.
