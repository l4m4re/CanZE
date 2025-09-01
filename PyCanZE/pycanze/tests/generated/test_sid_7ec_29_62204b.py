from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_62204b():
    client = ReplayUDSClient(sid_responses={"22204B": ['0462204B00AAAAAA']})
    assert client.read_field("7ec.29.62204b") == pytest.approx(0.0)
