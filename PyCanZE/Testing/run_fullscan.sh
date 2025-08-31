#!/usr/bin/env bash
set -euo pipefail

# Prompt for vehicle state and run a full scan, saving logs under Testing/logs.
# States: ready, charging, charger-connected-sleep, sleep

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
TOOLS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)/tools"

mkdir -p "$LOG_DIR"

echo "Select vehicle state:" >&2
echo "  1) ready" >&2
echo "  2) charging" >&2
echo "  3) charger-connected-sleep" >&2
echo "  4) sleep" >&2
STATE=""
while :; do
  read -r -p "Enter choice [1-4]: " CHOICE
  case "$CHOICE" in
    1) STATE="ready"; break ;;
    2) STATE="charging"; break ;;
    3) STATE="charger-connected-sleep"; break ;;
    4) STATE="sleep"; break ;;
    *) echo "Please enter a number between 1 and 4." >&2 ;;
  esac
done

TS="$(date +%Y%m%d-%H%M%S)"
RAW_OUT="$LOG_DIR/zoe-${STATE}-fullscan-${TS}.raw"
LOG_OUT="$LOG_DIR/zoe-${STATE}-fullscan-${TS}.log"

# Run from tools directory to match typical usage
pushd "$TOOLS_DIR" >/dev/null

# If you prefer a specific Python, set PYCANZE_PYTHON=/path/to/python before running
PYBIN="${PYCANZE_PYTHON:-python}"

set -x
START_TS="$(date +%s)"
"$PYBIN" scan_car.py ZOE \
  --only-values \
  --skip-nodata 0 \
  --per-ecu-limit 0 \
  --max-secs-per-ecu 0 \
  --raw-log "$RAW_OUT" | tee "$LOG_OUT"
END_TS="$(date +%s)"
set +x

popd >/dev/null

DUR_SEC=$((END_TS - START_TS))
H=$((DUR_SEC/3600))
M=$(((DUR_SEC%3600)/60))
S=$((DUR_SEC%60))
FMT=$(printf "%02d:%02d:%02d" "$H" "$M" "$S")
echo "Scan duration: ${FMT} (${DUR_SEC}s)" | tee -a "$LOG_OUT"

echo "Raw capture: $RAW_OUT"
echo "Pretty log : $LOG_OUT"
