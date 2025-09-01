from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623310():
    client = ReplayUDSClient(sid_responses={"223310": ['0462331000AAAAAA']})
    assert client.read_field("7ec.31.623310") == pytest.approx(0.0)
