from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_24_622032():
    client = ReplayUDSClient(sid_responses={"222032": ['0462203288000000']})
    assert client.read_field("76e.24.622032") == pytest.approx(13.6)
