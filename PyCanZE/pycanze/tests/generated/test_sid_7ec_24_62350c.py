from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62350c():
    client = ReplayUDSClient(sid_responses={"22350C": ['0462350C00AAAAAA']})
    assert client.read_field("7ec.24.62350c") == pytest.approx(0.0)
