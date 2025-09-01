from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_24_622033():
    client = ReplayUDSClient(sid_responses={"222033": ['0462203300000000']})
    assert client.read_field("76e.24.622033") == pytest.approx(0.0)
