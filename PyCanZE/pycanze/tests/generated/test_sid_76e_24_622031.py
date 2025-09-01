from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_24_622031():
    client = ReplayUDSClient(sid_responses={"222031": ['0462203188000000']})
    assert client.read_field("76e.24.622031") == pytest.approx(13.6)
