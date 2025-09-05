from __future__ import annotations

from typing import Dict, Optional, Any

# Diagnostic field identifiers used for state detection and payload building
SID_SOC = "7ec.24.622002"
SID_SOC_MEM = "7ec.168.623415"
SID_SOH = "7ec.24.623206"
SID_HV_V = "7ec.24.623203"
SID_ODO = "7ec.24.623200"  # some datasets use 7ec.24.622006
SID_CHG_MODE = "7ec.30.6234dd"
SID_CHG_SET = "7ec.24.6234ad"
SID_HVAC_REQ = "7ec.31.6233cd"
SID_HEAT_REQ = "7ec.25.623328"
SID_KEY_STATE = "7ec.31.62200e"

POLL_SIDS = [
    SID_SOC,
    SID_SOC_MEM,
    SID_SOH,
    SID_HV_V,
    SID_ODO,
    SID_CHG_MODE,
    SID_CHG_SET,
    SID_HVAC_REQ,
    SID_HEAT_REQ,
    SID_KEY_STATE,
]


def detect_state(vals: Dict[str, Optional[float]]) -> str:
    """Return vehicle state based on heuristic signals."""

    key = vals.get(SID_KEY_STATE)
    chg_mode = vals.get(SID_CHG_MODE)
    chg_set = vals.get(SID_CHG_SET)
    soc = vals.get(SID_SOC)
    hvac = vals.get(SID_HVAC_REQ)
    heat = vals.get(SID_HEAT_REQ)

    if key == 1:
        return "ready"
    if chg_mode == 2 or (chg_set is not None and chg_set > 0):
        return "charging"
    if soc == 0:
        if hvac == 1 or heat == 0:
            return "charger_connected_sleep"
        return "parked_sleep"
    return "parked"


def select_soc(soc: Optional[float], soc_mem: Optional[float]) -> Optional[float]:
    """Prefer memorised SOC when the direct read returns a sentinel."""

    if soc in (None, 0) and soc_mem not in (None, 0):
        return soc_mem
    return soc


def filter_soh(soh: Optional[float]) -> Optional[float]:
    """Discard implausible SOH readings."""

    if soh is None or soh > 100:
        return None
    return soh


def filter_hv_voltage(hv: Optional[float]) -> Optional[float]:
    """Discard placeholder HV voltage readings."""

    if hv is None or hv >= 500:
        return None
    return hv


def filter_odometer(odo: Optional[float]) -> Optional[int]:
    """Convert odometer to int, ignoring failures."""

    if odo is None:
        return None
    try:
        return int(odo)
    except Exception:
        return None


def build_payload(vals: Dict[str, Optional[float]], state: str) -> Dict[str, Any]:
    """Filter sentinel values and construct payload."""

    soc = select_soc(vals.get(SID_SOC), vals.get(SID_SOC_MEM))
    soh = filter_soh(vals.get(SID_SOH))
    hv = filter_hv_voltage(vals.get(SID_HV_V))
    odo = filter_odometer(vals.get(SID_ODO))

    data: Dict[str, Any] = {"state": state}
    if soc not in (None, 0):
        data["soc"] = round(float(soc), 3)
    if soh is not None:
        data["soh"] = round(float(soh), 3)
    if hv is not None:
        data["hv_voltage"] = round(float(hv), 3)
    if odo is not None:
        data["odometer"] = odo
    return data
