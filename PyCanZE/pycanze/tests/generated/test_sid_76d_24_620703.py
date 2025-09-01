from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620703():
    client = ReplayUDSClient(sid_responses={"220703": ['0462070314000000']})
    assert client.read_field("76d.24.620703") == pytest.approx(0.3)
