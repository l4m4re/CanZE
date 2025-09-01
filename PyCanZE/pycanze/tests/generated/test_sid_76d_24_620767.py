from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620767():
    client = ReplayUDSClient(sid_responses={"220767": ['0462076700000000']})
    assert client.read_field("76d.24.620767") == pytest.approx(0.0)
