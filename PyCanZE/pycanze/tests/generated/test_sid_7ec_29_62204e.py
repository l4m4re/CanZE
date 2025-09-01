from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_62204e():
    client = ReplayUDSClient(sid_responses={"22204E": ['0462204E20AAAAAA']})
    assert client.read_field("7ec.29.62204e") == pytest.approx(0.0)
