from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6234ff():
    client = ReplayUDSClient(sid_responses={"2234FF": ['046234FF00AAAAAA']})
    assert client.read_field("7ec.31.6234ff") == pytest.approx(0.0)
