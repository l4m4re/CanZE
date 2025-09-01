from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_62340a():
    client = ReplayUDSClient(sid_responses={"22340A": ['0462340A01AAAAAA']})
    assert client.read_field("7ec.30.62340a") == pytest.approx(1.0)
