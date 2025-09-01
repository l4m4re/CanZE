from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_62340e():
    client = ReplayUDSClient(sid_responses={"22340E": ['0462340E01AAAAAA']})
    assert client.read_field("7ec.30.62340e") == pytest.approx(1.0)
