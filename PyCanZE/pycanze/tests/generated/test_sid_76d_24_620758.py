from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620758():
    client = ReplayUDSClient(sid_responses={"220758": ['0462075801000000']})
    assert client.read_field("76d.24.620758") == pytest.approx(0.0)
