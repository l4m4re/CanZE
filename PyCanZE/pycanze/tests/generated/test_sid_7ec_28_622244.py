from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_28_622244():
    client = ReplayUDSClient(sid_responses={"222244": ['0462224400AAAAAA']})
    assert client.read_field("7ec.28.622244") == pytest.approx(0.0)
