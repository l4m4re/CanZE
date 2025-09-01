from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_622036():
    client = ReplayUDSClient(sid_responses={"222036": ['0462203600AAAAAA']})
    assert client.read_field("7ec.24.622036") == pytest.approx(0.0)
