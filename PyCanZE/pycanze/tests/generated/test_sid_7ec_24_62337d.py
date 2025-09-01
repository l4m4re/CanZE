from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62337d():
    client = ReplayUDSClient(sid_responses={"22337D": ['0462337D00AAAAAA']})
    assert client.read_field("7ec.24.62337d") == pytest.approx(0.0)
