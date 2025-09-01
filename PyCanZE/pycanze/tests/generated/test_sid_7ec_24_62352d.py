from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62352d():
    client = ReplayUDSClient(sid_responses={"22352D": ['0462352D00AAAAAA']})
    assert client.read_field("7ec.24.62352d") == pytest.approx(0.0)
