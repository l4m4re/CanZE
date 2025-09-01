from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_24_622012():
    client = ReplayUDSClient(sid_responses={"222012": ['0462201207000C0E']})
    assert client.read_field("76e.24.622012") == pytest.approx(7.0)
