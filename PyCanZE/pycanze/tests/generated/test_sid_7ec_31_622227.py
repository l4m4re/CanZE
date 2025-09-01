from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_622227():
    client = ReplayUDSClient(sid_responses={"222227": ['0462222700AAAAAA']})
    assert client.read_field("7ec.31.622227") == pytest.approx(0.0)
