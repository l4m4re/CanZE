from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623022():
    client = ReplayUDSClient(sid_responses={"223022": ['0462302200AAAAAA']})
    assert client.read_field("7ec.31.623022") == pytest.approx(0.0)
