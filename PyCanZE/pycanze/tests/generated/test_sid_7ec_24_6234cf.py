from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234cf():
    client = ReplayUDSClient(sid_responses={"2234CF": ['046234CF00AAAAAA']})
    assert client.read_field("7ec.24.6234cf") == pytest.approx(0.0)
