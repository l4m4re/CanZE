from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623417():
    client = ReplayUDSClient(sid_responses={"223417": ['056234170000AAAA']})
    assert client.read_field("7ec.31.623417") == pytest.approx(0.0)
