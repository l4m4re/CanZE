from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620752():
    client = ReplayUDSClient(sid_responses={"220752": ['0462075201000000']})
    assert client.read_field("76d.24.620752") == pytest.approx(0.0)
