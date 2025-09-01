from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_24_622004():
    client = ReplayUDSClient(sid_responses={"222004": ['0462200400302020']})
    assert client.read_field("76e.24.622004") == pytest.approx(0.0)
