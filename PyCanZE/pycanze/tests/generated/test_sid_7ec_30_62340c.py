from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_62340c():
    client = ReplayUDSClient(sid_responses={"22340C": ['0462340C01AAAAAA']})
    assert client.read_field("7ec.30.62340c") == pytest.approx(1.0)
