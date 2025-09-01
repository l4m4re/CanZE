from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623107():
    client = ReplayUDSClient(sid_responses={"223107": ['0462310702AAAAAA']})
    assert client.read_field("7ec.30.623107") == pytest.approx(2.0)
