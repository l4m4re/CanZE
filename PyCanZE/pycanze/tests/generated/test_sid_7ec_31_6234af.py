from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6234af():
    client = ReplayUDSClient(sid_responses={"2234AF": ['046234AF00AAAAAA']})
    assert client.read_field("7ec.31.6234af") == pytest.approx(0.0)
