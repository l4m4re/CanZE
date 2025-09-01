from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623335():
    client = ReplayUDSClient(sid_responses={"223335": ['0462333501AAAAAA']})
    assert client.read_field("7ec.30.623335") == pytest.approx(1.0)
