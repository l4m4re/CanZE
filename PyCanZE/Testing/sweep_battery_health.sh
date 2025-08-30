#!/usr/bin/env bash
# Sweep battery_health.py across timing and filter parameters
# Logs are stored under Testing/logs/battery_sweep_<timestamp>/

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_ROOT="$ROOT_DIR/Testing/logs"
TS="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="$LOG_ROOT/battery_sweep_${TS}"
mkdir -p "$OUT_DIR"

HOST=${1:-192.168.2.21}
PORT=${2:-35000}
CAR=${3:-ZOE}

CAF_VALUES=(0 1)
MASK_VALUES=(0 1) # 0 -> ATCRA, 1 -> ATCF/ATCM
STMIN_VALUES=(0 5)
HEADER_SETTLE_MS_VALUES=(0 100)
FIRST21_DELAY_MS_VALUES=(0 150)
LBC_FIRST21_DELAY_MS_VALUES=(0 150)
ATST_MS_VALUES=(0 40)
ISOTP_COLLECT_S_VALUES=(0.5 1.0)
CF_READ_TIMEOUT_S_VALUES=(0.1 0.3)
WIDE_CF_FALLBACK_VALUES=(0 1)

for caf in "${CAF_VALUES[@]}"; do
  for mask in "${MASK_VALUES[@]}"; do
    for stmin in "${STMIN_VALUES[@]}"; do
      for settle in "${HEADER_SETTLE_MS_VALUES[@]}"; do
        for first21 in "${FIRST21_DELAY_MS_VALUES[@]}"; do
          for lbc_first21 in "${LBC_FIRST21_DELAY_MS_VALUES[@]}"; do
            for atst in "${ATST_MS_VALUES[@]}"; do
              for collect in "${ISOTP_COLLECT_S_VALUES[@]}"; do
                for cftime in "${CF_READ_TIMEOUT_S_VALUES[@]}"; do
                  for wide in "${WIDE_CF_FALLBACK_VALUES[@]}"; do
                    log_file="$OUT_DIR/caf${caf}_mask${mask}_stmin${stmin}_settle${settle}_first21${first21}_lbcfirst21${lbc_first21}_atst${atst}_collect${collect}_cftime${cftime}_wide${wide}.log"
                    cmd=(python3 "$ROOT_DIR/tools/battery_health.py" "$CAR" --host "$HOST" --port "$PORT" --caf "$caf" --stmin-ms "$stmin" --header-settle-ms "$settle" --first-21-delay-ms "$first21" --lbc-first-21-delay-ms "$lbc_first21" --atst-ms "$atst" --isotp-collect-s "$collect" --cf-read-timeout-s "$cftime")
                    if [[ "$mask" -eq 1 ]]; then
                      cmd+=(--use-mask-filter)
                    fi
                    if [[ "$wide" -eq 1 ]]; then
                      cmd+=(--wide-cf-fallback)
                    fi
                    "${cmd[@]}" >"$log_file" 2>&1 || true
                  done
                done
              done
            done
          done
        done
      done
    done
  done
 done

echo "Logs written to $OUT_DIR"
