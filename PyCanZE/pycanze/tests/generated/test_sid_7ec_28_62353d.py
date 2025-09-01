from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_28_62353d():
    client = ReplayUDSClient(sid_responses={"22353D": ['0462353D00AAAAAA']})
    assert client.read_field("7ec.28.62353d") == pytest.approx(0.0)
