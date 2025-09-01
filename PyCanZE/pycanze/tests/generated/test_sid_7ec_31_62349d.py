from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62349d():
    client = ReplayUDSClient(sid_responses={"22349D": ['0462349D00AAAAAA']})
    assert client.read_field("7ec.31.62349d") == pytest.approx(0.0)
