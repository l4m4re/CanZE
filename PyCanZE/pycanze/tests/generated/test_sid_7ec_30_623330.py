from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623330():
    client = ReplayUDSClient(sid_responses={"223330": ['0462333000AAAAAA']})
    assert client.read_field("7ec.30.623330") == pytest.approx(0.0)
