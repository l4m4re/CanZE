from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234fb():
    client = ReplayUDSClient(sid_responses={"2234FB": ['046234FB00AAAAAA']})
    assert client.read_field("7ec.24.6234fb") == pytest.approx(0.0)
