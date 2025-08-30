# Testing utilities

This directory contains experimental utilities for validating CanZE's Python
UDS client.

## `sweep_battery_health.sh`

`sweep_battery_health.sh` runs `tools/battery_health.py` across a matrix of
ELM327 and ISO-TP timing parameters. Each combination is logged under
`logs/battery_sweep_<timestamp>/`.

### Usage

```bash
./sweep_battery_health.sh [host] [port] [car]
```

- `host` – ELM327 IP (default: `192.168.2.21`)
- `port` – ELM327 TCP port (default: `35000`)
- `car` – vehicle asset folder (default: `ZOE`)

### Parameters swept

The script iterates over:

- **CAF**: `ATCAF0` and `ATCAF1`
- **Mask filter usage**: `ATCRA` vs `ATCF`/`ATCM`
- **Flow control STmin**: `0` and `5` ms
- **Header settle delay**: `0` and `100` ms
- **First 0x21 delay**: `0` and `150` ms per ECU
- **LBC first 0x21 delay**: `0` and `150` ms
- **ATST timeout**: `0` and `40` ms
- **ISO‑TP collect window**: `0.5` s and `1.0` s
- **Consecutive‑frame read timeout**: `0.1` s and `0.3` s

Each run produces a log file named after the parameter values.
