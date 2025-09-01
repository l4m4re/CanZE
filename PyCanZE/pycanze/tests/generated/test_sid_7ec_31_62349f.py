from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62349f():
    client = ReplayUDSClient(sid_responses={"22349F": ['0462349F00AAAAAA']})
    assert client.read_field("7ec.31.62349f") == pytest.approx(0.0)
