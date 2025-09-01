from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62204d():
    client = ReplayUDSClient(sid_responses={"22204D": ['0462204D00AAAAAA']})
    assert client.read_field("7ec.31.62204d") == pytest.approx(0.0)
