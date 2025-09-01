from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_62340f():
    client = ReplayUDSClient(sid_responses={"22340F": ['0462340F01AAAAAA']})
    assert client.read_field("7ec.30.62340f") == pytest.approx(1.0)
