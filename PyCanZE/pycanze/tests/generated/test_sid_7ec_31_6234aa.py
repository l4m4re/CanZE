from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6234aa():
    client = ReplayUDSClient(sid_responses={"2234AA": ['046234AA00AAAAAA']})
    assert client.read_field("7ec.31.6234aa") == pytest.approx(0.0)
