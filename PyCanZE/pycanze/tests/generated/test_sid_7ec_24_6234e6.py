from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234e6():
    client = ReplayUDSClient(sid_responses={"2234E6": ['046234E600AAAAAA']})
    assert client.read_field("7ec.24.6234e6") == pytest.approx(0.0)
