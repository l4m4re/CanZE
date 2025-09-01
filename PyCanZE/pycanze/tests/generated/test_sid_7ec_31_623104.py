from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623104():
    client = ReplayUDSClient(sid_responses={"223104": ['0462310400AAAAAA']})
    assert client.read_field("7ec.31.623104") == pytest.approx(0.0)
