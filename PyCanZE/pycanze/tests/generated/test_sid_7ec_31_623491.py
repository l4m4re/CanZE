from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623491():
    client = ReplayUDSClient(sid_responses={"223491": ['0462349100AAAAAA']})
    assert client.read_field("7ec.31.623491") == pytest.approx(0.0)
