from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62345d():
    client = ReplayUDSClient(sid_responses={"22345D": ['0462345D00AAAAAA']})
    assert client.read_field("7ec.24.62345d") == pytest.approx(0.0)
