from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_24_622006():
    client = ReplayUDSClient(sid_responses={"222006": ['0662200600B74DAA']})
    assert client.read_field("76e.24.622006") == pytest.approx(0.0)
