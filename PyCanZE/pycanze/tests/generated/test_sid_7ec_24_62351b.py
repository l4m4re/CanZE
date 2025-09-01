from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62351b():
    client = ReplayUDSClient(sid_responses={"22351B": ['0462351B3CAAAAAA']})
    assert client.read_field("7ec.24.62351b") == pytest.approx(20.0)
