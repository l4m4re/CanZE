from __future__ import annotations

from . import mk_replay_client


def detect_state(client):
    """Return (state, soc) from canned diagnostic fields."""

    soc = client.read_field("soc")
    pump = client.read_field("pump")
    if pump and pump > 0:
        return "charging", soc
    if soc == 0:
        return "charger_connected_sleep", None
    return "ready", soc


def test_ready_state(mk_replay_client):
    client = mk_replay_client({
        "222002": ["056220020050"],  # SOC 80%
        "223319": ["0462331900"],   # pump idle
    })
    state, soc = detect_state(client)
    assert state == "ready"
    assert soc == 80


def test_charging_state(mk_replay_client):
    client = mk_replay_client({
        "222002": ["056220020028"],  # SOC 40%
        "223319": ["046233190A"],   # pump active
    })
    state, soc = detect_state(client)
    assert state == "charging"
    assert soc == 40


def test_charger_connected_sleep_sentinel(mk_replay_client):
    client = mk_replay_client({
        "222002": ["056220020000"],  # SOC sentinel 0%
        "223319": ["0462331900"],   # pump idle
    })
    state, soc = detect_state(client)
    assert state == "charger_connected_sleep"
    assert soc is None
