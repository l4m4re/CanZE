from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_24_622010():
    client = ReplayUDSClient(sid_responses={"222010": ['0462201005000C0E']})
    assert client.read_field("76e.24.622010") == pytest.approx(5.0)
