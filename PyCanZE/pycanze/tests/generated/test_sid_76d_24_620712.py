from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620712():
    client = ReplayUDSClient(sid_responses={"220712": ['0462071200000000']})
    assert client.read_field("76d.24.620712") == pytest.approx(0.0)
