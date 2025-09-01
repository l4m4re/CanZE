from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62352f():
    client = ReplayUDSClient(sid_responses={"22352F": ['0462352F28AAAAAA']})
    assert client.read_field("7ec.24.62352f") == pytest.approx(0.0)
