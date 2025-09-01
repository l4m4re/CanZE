from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623006():
    client = ReplayUDSClient(sid_responses={"223006": ['0462300601AAAAAA']})
    assert client.read_field("7ec.30.623006") == pytest.approx(1.0)
