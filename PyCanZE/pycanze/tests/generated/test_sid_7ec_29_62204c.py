from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_62204c():
    client = ReplayUDSClient(sid_responses={"22204C": ['0462204C00AAAAAA']})
    assert client.read_field("7ec.29.62204c") == pytest.approx(0.0)
