from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6233ce():
    client = ReplayUDSClient(sid_responses={"2233CE": ['046233CE00AAAAAA']})
    assert client.read_field("7ec.31.6233ce") == pytest.approx(0.0)
