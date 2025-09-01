from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6234da():
    client = ReplayUDSClient(sid_responses={"2234DA": ['046234DA00AAAAAA']})
    assert client.read_field("7ec.31.6234da") == pytest.approx(0.0)
