from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623461():
    client = ReplayUDSClient(sid_responses={"223461": ['0462346100AAAAAA']})
    assert client.read_field("7ec.31.623461") == pytest.approx(0.0)
