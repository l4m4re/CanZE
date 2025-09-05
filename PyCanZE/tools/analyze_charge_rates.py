#!/usr/bin/env python3
"""Analyze poller CSV logs to estimate charging rate (%/hour) per current setting.

The script:
- Reads one or more CSV log files from the poller.
- Segments contiguous charging periods where the measured current maps to a
  nominal EVSE setting (6, 8, 10, 13, 16 A, configurable).
- Uses linear regression on SoC vs time (hours) for each segment to compute a
  robust slope in %/hour.
- Filters short/noisy segments (min duration and min ΔSoC configurable).
- Prints per-segment stats and aggregated per-setting summaries (weighted avg).

Inputs expected from the poller CSV header (best effort):
- timestamp (ISO8601), state, charging
- soc, soc_mem
- chg_set_A (PEB setpoint A) [used to determine the nominal setting]
- shelly_current_a (measured A) if present; else measured A ≈ shelly_apower_w / shelly_voltage_v

Usage:
    python analyze_charge_rates.py --logs <file_or_dir>
    # Recommended: focus on mid-SOC to avoid taper and edge effects
    python analyze_charge_rates.py --soc-range 20,80 --min-duration 600 --min-soc-delta 1.0
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Dict, Optional, Tuple


DEFAULT_SETTINGS = [6, 8, 10, 13, 16]


@dataclass
class Sample:
    ts: datetime
    charging: bool
    soc: Optional[float]
    soc_mem: Optional[float]
    setpoint_a: Optional[float]
    shelly_current_a: Optional[float]
    shelly_apower_w: Optional[float]
    shelly_voltage_v: Optional[float]
    shelly_aenergy_total_Wh: Optional[float] = None

    @property
    def soc_pref(self) -> Optional[float]:
        return self.soc if self.soc is not None else self.soc_mem

    @property
    def measured_a(self) -> Optional[float]:
        if self.shelly_current_a is not None:
            return self.shelly_current_a
        if self.shelly_apower_w is not None and self.shelly_voltage_v is not None and self.shelly_voltage_v > 10:
            try:
                return float(self.shelly_apower_w) / float(self.shelly_voltage_v)
            except Exception:
                return None
        return None

    @property
    def measured_power_w(self) -> Optional[float]:
        # Prefer Shelly active power; else compute V*I if both available
        if self.shelly_apower_w is not None:
            return self.shelly_apower_w
        ia = self.shelly_current_a
        v = self.shelly_voltage_v
        if ia is not None and v is not None and v > 10:
            try:
                return float(ia) * float(v)
            except Exception:
                return None
        return None

    @property
    def aenergy_kwh(self) -> Optional[float]:
        # Shelly aenergy.total is Wh; convert to kWh
        if self.shelly_aenergy_total_Wh is None:
            return None
        try:
            return float(self.shelly_aenergy_total_Wh) / 1000.0
        except Exception:
            return None


@dataclass
class Segment:
    setting: int
    samples: List[Sample]

    def _filtered(self, soc_low: Optional[float], soc_high: Optional[float]) -> List[Sample]:
        if soc_low is None and soc_high is None:
            return [s for s in self.samples if s.soc_pref is not None]
        flt: List[Sample] = []
        for s in self.samples:
            sp = s.soc_pref
            if sp is None:
                continue
            if soc_low is not None and sp < soc_low:
                continue
            if soc_high is not None and sp > soc_high:
                continue
            flt.append(s)
        return flt

    def stats(self, soc_low: Optional[float], soc_high: Optional[float]) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
        """Return (duration_seconds, d_soc, slope_pct_per_hour, avg_measured_a) on filtered points."""
        pts = self._filtered(soc_low, soc_high)
        if len(pts) < 2:
            return (None, None, None, None)
        t0 = pts[0].ts
        tN = pts[-1].ts
        xs: List[float] = []
        ys: List[float] = []
        amps: List[float] = []
        for s in pts:
            xs.append((s.ts - t0).total_seconds() / 3600.0)
            ys.append(float(s.soc_pref))
            if s.measured_a is not None:
                amps.append(float(s.measured_a))
        if len(xs) < 2:
            return (None, None, None, None)
        mean_x = sum(xs) / len(xs)
        mean_y = sum(ys) / len(ys)
        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
        den = sum((x - mean_x) ** 2 for x in xs)
        if den <= 0:
            return (None, None, None, None)
        slope = num / den
        dur_s = (tN - t0).total_seconds()
        d_soc = ys[-1] - ys[0]
        avg_a = (sum(amps) / len(amps)) if amps else None
        return (dur_s, d_soc, slope, avg_a)

    def wall_energy_kwh(self, soc_low: Optional[float], soc_high: Optional[float]) -> Optional[float]:
        """Wall energy for the segment.

        Prefer using Shelly cumulative energy deltas when available on both ends.
        Otherwise, fall back to trapezoidal integration of measured power.
        """
        pts = self._filtered(soc_low, soc_high)
        if len(pts) < 2:
            return None
        # Try cumulative energy first
        a0 = pts[0].aenergy_kwh
        aN = pts[-1].aenergy_kwh
        if a0 is not None and aN is not None and aN > a0:
            return aN - a0
        e_kwh = 0.0
        prev = pts[0]
        for cur in pts[1:]:
            dt_h = (cur.ts - prev.ts).total_seconds() / 3600.0
            if dt_h <= 0:
                prev = cur
                continue
            p1 = prev.measured_power_w
            p2 = cur.measured_power_w
            if p1 is None and p2 is None:
                prev = cur
                continue
            if p1 is None:
                p_avg_w = p2
            elif p2 is None:
                p_avg_w = p1
            else:
                p_avg_w = 0.5 * (p1 + p2)
            e_kwh += (p_avg_w / 1000.0) * dt_h
            prev = cur
        return e_kwh if e_kwh > 0 else None

    def wall_energy_stats(self, soc_low: Optional[float], soc_high: Optional[float]) -> Tuple[Optional[float], float]:
        """Return (energy_kwh, coverage) where coverage is time fraction with usable power data.

        If cumulative energy is available on both ends, returns that energy with coverage=1.0.
        """
        pts = self._filtered(soc_low, soc_high)
        if len(pts) < 2:
            return (None, 0.0)
        # Prefer cumulative energy
        a0 = pts[0].aenergy_kwh
        aN = pts[-1].aenergy_kwh
        if a0 is not None and aN is not None and aN > a0:
            return (aN - a0, 1.0)
        e_kwh = 0.0
        covered_h = 0.0
        total_h = 0.0
        prev = pts[0]
        for cur in pts[1:]:
            dt_h = (cur.ts - prev.ts).total_seconds() / 3600.0
            if dt_h <= 0:
                prev = cur
                continue
            total_h += dt_h
            p1 = prev.measured_power_w
            p2 = cur.measured_power_w
            if p1 is None and p2 is None:
                prev = cur
                continue
            if p1 is None:
                p_avg_w = p2
            elif p2 is None:
                p_avg_w = p1
            else:
                p_avg_w = 0.5 * (p1 + p2)
            e_kwh += (p_avg_w / 1000.0) * dt_h
            covered_h += dt_h
            prev = cur
        coverage = (covered_h / total_h) if total_h > 0 else 0.0
        return ((e_kwh if e_kwh > 0 else None), coverage)

    def stored_energy_kwh(
        self,
        soc_low: Optional[float],
        soc_high: Optional[float],
        effective_capacity_kwh: float,
        method: str = "slope",
    ) -> Optional[float]:
        """Estimate stored energy using either regression slope or endpoints ΔSoC within the filtered window.

        method:
        - 'slope': use linear regression slope (%/h) times duration (h)
        - 'endpoints': use last-first SoC
        """
        pts = self._filtered(soc_low, soc_high)
        if len(pts) < 2:
            return None
        if method == "endpoints":
            try:
                dsoc = float(pts[-1].soc_pref) - float(pts[0].soc_pref)
            except Exception:
                return None
            if dsoc <= 0:
                return None
            return (dsoc / 100.0) * effective_capacity_kwh
        # slope method
        dur_s, d_soc, slope, _ = self.stats(soc_low, soc_high)
        if slope is None or dur_s is None:
            return None
        dur_h = dur_s / 3600.0
        dsoc = slope * dur_h
        if dsoc <= 0:
            return None
        return (dsoc / 100.0) * effective_capacity_kwh


def parse_bool(v: str) -> Optional[bool]:
    if v is None:
        return None
    t = v.strip().lower()
    if t in ("1", "true", "yes"):
        return True
    if t in ("0", "false", "no"):
        return False
    return None


def parse_float(v: str) -> Optional[float]:
    try:
        if v is None or v == "":
            return None
        return float(v)
    except Exception:
        return None


def load_samples(csv_path: Path) -> List[Sample]:
    rows: List[Sample] = []
    with csv_path.open("r", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                ts = datetime.fromisoformat(row.get("timestamp", ""))
            except Exception:
                continue
            charging = parse_bool(row.get("charging")) or False
            soc = parse_float(row.get("soc"))
            soc_mem = parse_float(row.get("soc_mem"))
            set_a = parse_float(row.get("chg_set_A"))
            shelly_i = parse_float(row.get("shelly_current_a"))
            shelly_p = parse_float(row.get("shelly_apower_w"))
            shelly_v = parse_float(row.get("shelly_voltage_v"))
            shelly_e = parse_float(row.get("shelly_aenergy_total_Wh"))
            rows.append(Sample(ts, charging, soc, soc_mem, set_a, shelly_i, shelly_p, shelly_v, shelly_e))
    rows.sort(key=lambda s: s.ts)
    return rows


def nearest_setting(current_a: float, settings: List[int]) -> int:
    return min(settings, key=lambda s: abs(current_a - s))


def segment_charging(samples: List[Sample], settings: List[int]) -> List[Segment]:
    segs: List[Segment] = []
    cur_seg: Optional[Segment] = None
    for s in samples:
        if not s.charging:
            if cur_seg and cur_seg.samples:
                segs.append(cur_seg)
            cur_seg = None
            continue
        # Prefer measured current (Shelly) to determine nominal; fallback to setpoint
        nominal: Optional[int] = None
        meas = s.measured_a
        if meas is not None and meas > 0:
            nominal = nearest_setting(meas, settings)
        elif s.setpoint_a is not None and s.setpoint_a > 0:
            nominal = nearest_setting(s.setpoint_a, settings)
        if nominal is None:
            # break segment if we cannot classify
            if cur_seg and cur_seg.samples:
                segs.append(cur_seg)
            cur_seg = None
            continue
        if cur_seg is None:
            cur_seg = Segment(nominal, [s])
            continue
        # If setting changes, close previous and start new
        if nominal != cur_seg.setting:
            segs.append(cur_seg)
            cur_seg = Segment(nominal, [s])
        else:
            cur_seg.samples.append(s)
    if cur_seg and cur_seg.samples:
        segs.append(cur_seg)
    return segs


def filter_segments(
    segs: List[Segment],
    min_duration_s: float,
    min_soc_delta_pct: float,
    soc_low: Optional[float],
    soc_high: Optional[float],
    require_positive_dsoc: bool,
) -> List[Segment]:
    out: List[Segment] = []
    for seg in segs:
        dur, d_soc, slope, _ = seg.stats(soc_low, soc_high)
        if dur is None or d_soc is None or slope is None:
            continue
        if dur < min_duration_s:
            continue
        if abs(d_soc) < min_soc_delta_pct:
            continue
        if require_positive_dsoc and d_soc <= 0:
            continue
        if slope <= 0:
            continue
        out.append(seg)
    return out


def summarize_by_setting(
    segs: List[Segment], soc_low: Optional[float], soc_high: Optional[float], current_tolerance: float, require_measured: bool
) -> Dict[int, Dict[str, float]]:
    # Weighted average by duration; also compute simple mean and avg measured current
    summary: Dict[int, Dict[str, float]] = {}
    by_setting: Dict[int, List[Tuple[float, float, float]]] = {}
    # list of (slope, duration_h, avg_meas)
    for seg in segs:
        dur_s, d_soc, slope, avg_i = seg.stats(soc_low, soc_high)
        if slope is None or dur_s is None:
            continue
        # If we have measured current, ensure it matches the nominal setting reasonably
        if require_measured and avg_i is None:
            continue
        if avg_i is not None and seg.setting > 0:
            if abs(avg_i - seg.setting) > current_tolerance * seg.setting:
                continue
        dur_h = dur_s / 3600.0
        by_setting.setdefault(seg.setting, []).append((slope, dur_h, (avg_i or 0.0)))

    for setting, vals in by_setting.items():
        total_h = sum(v[1] for v in vals)
        wavg = sum(v[0] * v[1] for v in vals) / total_h if total_h > 0 else float("nan")
        mean = sum(v[0] for v in vals) / len(vals)
        avg_i = sum(v[2] * v[1] for v in vals) / total_h if total_h > 0 else float("nan")
        summary[setting] = {
            "segments": float(len(vals)),
            "total_hours": total_h,
            "rate_pct_per_hour_weighted": wavg,
            "rate_pct_per_hour_mean": mean,
            "avg_measured_a": avg_i,
        }
    return summary


def discover_csvs(input_path: Path) -> List[Path]:
    if input_path.is_file():
        return [input_path]
    if input_path.is_dir():
        return sorted(input_path.glob("*.csv"))
    return []


def main() -> None:
    p = argparse.ArgumentParser(description="Compute charging rate (%%/hour) per EVSE current setting from poller CSV logs")
    p.add_argument("--logs", default=str(Path(__file__).resolve().parents[1] / "Testing" / "logs"), help="Path to a CSV file or a directory of CSVs")
    p.add_argument("--min-duration", type=float, default=600.0, help="Min segment duration in seconds")
    p.add_argument("--min-soc-delta", type=float, default=1.0, help="Min absolute SOC change (percentage points) per segment")
    p.add_argument("--settings", default=",".join(str(s) for s in DEFAULT_SETTINGS), help="Comma-separated EVSE nominal settings to bin by")
    p.add_argument("--print-segments", action="store_true", help="Print individual segment stats")
    p.add_argument("--current-tolerance", type=float, default=0.25, help="Allowed relative deviation of measured current from nominal setting to include a segment (0.25=±25%)")
    p.add_argument(
        "--require-measured",
        action="store_true",
        default=True,
        help="Require measured current (Shelly) to include a segment in summary (default: on)",
    )
    p.add_argument(
        "--allow-unmeasured",
        action="store_true",
        help="Include segments without measured current (overrides --require-measured default)",
    )
    p.add_argument("--require-positive-dsoc", action="store_true", help="Filter out charging segments where ΔSoC ≤ 0")
    p.add_argument("--soc-range", default="20,80", help="SOC range to consider for slope (e.g., 20,80). Empty to disable.")
    p.add_argument("--nominal-kwh", type=float, default=41.0, help="Original nominal battery capacity in kWh")
    p.add_argument(
        "--soh",
        default="0.90,0.921",
        help="SOH fraction(s), comma-separated (e.g., '0.90,0.921'). Used to compute efficiency with multiple SOH assumptions.",
    )
    p.add_argument(
        "--stored-method",
        choices=["slope", "endpoints"],
        default="slope",
        help="Method to compute stored energy: regression slope (default) or endpoints",
    )
    p.add_argument("--min-energy-coverage", type=float, default=0.8, help="Minimum fraction of time with usable power data to include in efficiency (0-1)")
    args = p.parse_args()
    if getattr(args, "allow_unmeasured", False):
        args.require_measured = False

    settings = [int(s.strip()) for s in args.settings.split(",") if s.strip()]
    # Parse SOH list
    soh_list: List[float] = []
    try:
        for tok in str(args.soh).split(","):
            tok = tok.strip()
            if not tok:
                continue
            soh_list.append(float(tok))
    except Exception:
        soh_list = [0.90]
    if not soh_list:
        soh_list = [0.90]
    logs_path = Path(args.logs)
    csv_paths = discover_csvs(logs_path)
    if not csv_paths:
        print(f"No CSV files found under {logs_path}")
        return

    # SOC window
    soc_low: Optional[float]
    soc_high: Optional[float]
    try:
        if args.soc_range.strip():
            parts = [p.strip() for p in args.soc_range.split(",")]
            soc_low = float(parts[0]) if parts and parts[0] else None
            soc_high = float(parts[1]) if len(parts) > 1 and parts[1] else None
        else:
            soc_low = soc_high = None
    except Exception:
        soc_low = 20.0
        soc_high = 80.0

    all_segments: List[Segment] = []
    for path in csv_paths:
        try:
            samples = load_samples(path)
        except Exception as e:
            print(f"Skipping {path.name}: {e}")
            continue
        segs = segment_charging(samples, settings)
        segs = filter_segments(
            segs, args.min_duration, args.min_soc_delta, soc_low, soc_high, args.require_positive_dsoc
        )
        if args.print_segments:
            for s in segs:
                dur, d_soc, slope, avg_i = s.stats(soc_low, soc_high)
                if dur is None or d_soc is None or slope is None:
                    continue
                dur_min = dur / 60.0
                i_str = "n/a" if avg_i is None else f"{avg_i:.2f}A"
                wall_kwh, coverage = s.wall_energy_stats(soc_low, soc_high)
                # Compute efficiencies for all SOH assumptions
                eff_parts: List[str] = []
                for soh in soh_list:
                    stored_kwh_i = s.stored_energy_kwh(soc_low, soc_high, args.nominal_kwh * soh, args.stored_method)
                    eff_i = (stored_kwh_i / wall_kwh) if (wall_kwh and wall_kwh > 0 and stored_kwh_i) else None
                    label = f"@{int(round(soh*100))}%"
                    eff_parts.append("n/a" if eff_i is None else f"{eff_i*100:.1f}%{label}")
                eff_str = ", ".join(eff_parts)
                wall_str = "n/a" if wall_kwh is None else f"{wall_kwh:.2f}kWh"
                # Omit per-SOH stored_kwh details to keep line compact
                st_str = "—"
                cov_str = f"{coverage*100:.0f}%"
                print(
                    f"{path.name} setting={s.setting:>2}A  duration={dur_min:.1f} min  "
                    f"ΔSoC={d_soc:.2f}%  rate={slope:.2f} %/h  Iavg={i_str}  Wall={wall_str}  Stored={st_str}  Eff[{eff_str}]  Cov={cov_str}"
                )
        all_segments.extend(segs)

    summary = summarize_by_setting(all_segments, soc_low, soc_high, args.current_tolerance, args.require_measured)
    if not summary:
        print("No qualifying segments found.")
        return

    # Print summary sorted by setting
    print("\nCharging rate summary (by EVSE setting)")
    print("setting  segs  hours   rate_wavg(%/h)  rate_mean(%/h)  Iavg(A)")
    for setting in sorted(summary.keys()):
        s = summary[setting]
        print(
            f"{setting:>7}  {int(s['segments']):>4}  {s['total_hours']:>5.2f}   "
            f"{s['rate_pct_per_hour_weighted']:>14.2f}  {s['rate_pct_per_hour_mean']:>14.2f}  {s['avg_measured_a']:>7.2f}"
        )

    # Efficiency summaries per SOH
    for soh in soh_list:
        eff_data: Dict[int, List[Tuple[float, float]]] = {}
        for seg in all_segments:
            dur, d_soc, slope, avg_i = seg.stats(soc_low, soc_high)
            wall_kwh, coverage = seg.wall_energy_stats(soc_low, soc_high)
            stored_kwh = seg.stored_energy_kwh(soc_low, soc_high, args.nominal_kwh * soh, args.stored_method)
            # Require positive endpoint ΔSoC, usable wall/stored energy, and sufficient coverage
            if (
                d_soc is None or d_soc <= 0 or wall_kwh is None or wall_kwh <= 0 or stored_kwh is None or stored_kwh <= 0 or coverage < args.min_energy_coverage
            ):
                continue
            eff = stored_kwh / wall_kwh if wall_kwh > 0 else None
            if eff is None:
                continue
            eff_data.setdefault(seg.setting, []).append((eff, wall_kwh))

        if eff_data:
            print(f"\nCharge efficiency (by EVSE setting) — SOH={soh*100:.1f}%")
            print("setting  segs  wall_kWh  eff_wavg(%)  eff_mean(%)")
            for setting in sorted(eff_data.keys()):
                vals = eff_data[setting]
                total_wall = sum(v[1] for v in vals)
                wavg = sum(v[0] * v[1] for v in vals) / total_wall if total_wall > 0 else float('nan')
                mean = sum(v[0] for v in vals) / len(vals)
                print(
                    f"{setting:>7}  {len(vals):>4}  {total_wall:>8.2f}  {wavg*100:>11.1f}  {mean*100:>11.1f}"
                )


if __name__ == "__main__":
    main()
