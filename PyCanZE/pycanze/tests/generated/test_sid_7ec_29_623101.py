from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_623101():
    client = ReplayUDSClient(sid_responses={"223101": ['0462310100AAAAAA']})
    assert client.read_field("7ec.29.623101") == pytest.approx(0.0)
