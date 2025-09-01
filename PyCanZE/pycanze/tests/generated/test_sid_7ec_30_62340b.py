from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_62340b():
    client = ReplayUDSClient(sid_responses={"22340B": ['0462340B01AAAAAA']})
    assert client.read_field("7ec.30.62340b") == pytest.approx(1.0)
