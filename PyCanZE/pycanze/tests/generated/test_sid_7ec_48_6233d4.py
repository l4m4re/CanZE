from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_48_6233d4():
    client = ReplayUDSClient(sid_responses={"2233D4": ['10216233D400B5FB', '2100B5FB00B5FB00', '22B60000B69B00B6', '23FA00B71E00B71E', '2400B71E00B71EAA']})
    assert client.read_field("7ec.48.6233d4") == pytest.approx(46587.0)
