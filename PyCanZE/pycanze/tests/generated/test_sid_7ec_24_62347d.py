from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62347d():
    client = ReplayUDSClient(sid_responses={"22347D": ['0462347D00AAAAAA']})
    assert client.read_field("7ec.24.62347d") == pytest.approx(0.0)
