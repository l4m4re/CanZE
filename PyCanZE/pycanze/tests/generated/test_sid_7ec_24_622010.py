from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_622010():
    client = ReplayUDSClient(sid_responses={"222010": ['0462201000AAAAAA']})
    assert client.read_field("7ec.24.622010") == pytest.approx(0.0)
