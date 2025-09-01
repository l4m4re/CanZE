from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_24_622016():
    client = ReplayUDSClient(sid_responses={"222016": ['0462201605000C0E']})
    assert client.read_field("76e.24.622016") == pytest.approx(5.0)
