from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_25_623327():
    client = ReplayUDSClient(sid_responses={"223327": ['046233270AAAAAAA']})
    assert client.read_field("7ec.25.623327") == pytest.approx(10.0)
