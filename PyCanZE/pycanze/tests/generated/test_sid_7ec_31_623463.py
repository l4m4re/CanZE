from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623463():
    client = ReplayUDSClient(sid_responses={"223463": ['0462346300AAAAAA']})
    assert client.read_field("7ec.31.623463") == pytest.approx(0.0)
