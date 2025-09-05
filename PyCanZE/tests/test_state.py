from __future__ import annotations

from typing import Dict

from pycanze.models import Field
from pycanze.replay_client import ReplayClient
from pycanze import state as st


def _mk_field(sid: str, request_id: str, width: int) -> Field:
    start_bit = 24
    end_bit = start_bit + width * 8 - 1
    return Field(
        sid=sid,
        frame_id=0x7EC,
        start_bit=start_bit,
        end_bit=end_bit,
        resolution=1.0,
        offset=0.0,
        decimals=0,
        unit="",
        request_id=request_id,
        response_id=None,
        options=0,
    )


FIELDS: Dict[str, Field] = {
    st.SID_SOC: _mk_field(st.SID_SOC, "222002", 2),
    st.SID_SOC_MEM: _mk_field(st.SID_SOC_MEM, "223415", 2),
    st.SID_SOH: _mk_field(st.SID_SOH, "223206", 1),
    st.SID_HV_V: _mk_field(st.SID_HV_V, "223203", 2),
    st.SID_ODO: _mk_field(st.SID_ODO, "223200", 1),
    st.SID_CHG_MODE: _mk_field(st.SID_CHG_MODE, "2234DD", 1),
    st.SID_CHG_SET: _mk_field(st.SID_CHG_SET, "2234AD", 2),
    st.SID_HVAC_REQ: _mk_field(st.SID_HVAC_REQ, "2233CD", 1),
    st.SID_HEAT_REQ: _mk_field(st.SID_HEAT_REQ, "223328", 1),
    st.SID_KEY_STATE: _mk_field(st.SID_KEY_STATE, "22200E", 1),
}


def _encode(req: str, val: int, size: int) -> str:
    did = req[2:]
    length = 4 if size == 1 else 5
    data = f"{val:0{size * 2}X}"
    return f"{length:02X}62{did}{data}"


def make_client(values: Dict[str, int]) -> ReplayClient:
    responses = {}
    for sid, field in FIELDS.items():
        req = field.request_id or ""
        width = field.end_bit - field.start_bit + 1
        size = 2 if width > 8 else 1
        val = values.get(sid, 0)
        responses[req] = [_encode(req, int(val), size)]
    return ReplayClient(sid_responses=responses, fields=FIELDS)


def gather(client: ReplayClient) -> Dict[str, float | None]:
    return {sid: client.read_field(sid) for sid in st.POLL_SIDS}


def test_ready_state():
    client = make_client({
        st.SID_KEY_STATE: 1,
        st.SID_SOC: 80,
        st.SID_SOC_MEM: 80,
    })
    vals = gather(client)
    state = st.detect_state(vals)
    payload = st.build_payload(vals, state)
    assert state == "ready"
    assert payload["soc"] == 80


def test_charging_state():
    client = make_client({
        st.SID_CHG_MODE: 2,
        st.SID_SOC: 40,
        st.SID_SOC_MEM: 40,
    })
    vals = gather(client)
    state = st.detect_state(vals)
    payload = st.build_payload(vals, state)
    assert state == "charging"
    assert payload["soc"] == 40


def test_sleep_state_uses_mem_soc():
    client = make_client({
        st.SID_SOC: 0,
        st.SID_SOC_MEM: 70,
        st.SID_HVAC_REQ: 1,
        st.SID_HEAT_REQ: 0,
    })
    vals = gather(client)
    state = st.detect_state(vals)
    payload = st.build_payload(vals, state)
    assert state == "charger_connected_sleep"
    assert payload["soc"] == 70
