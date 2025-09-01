from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620750():
    client = ReplayUDSClient(sid_responses={"220750": ['0462075003000000']})
    assert client.read_field("76d.24.620750") == pytest.approx(0.0)
