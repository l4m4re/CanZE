from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62351e():
    client = ReplayUDSClient(sid_responses={"22351E": ['0462351E01AAAAAA']})
    assert client.read_field("7ec.24.62351e") == pytest.approx(1.0)
