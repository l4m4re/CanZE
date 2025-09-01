from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62331d():
    client = ReplayUDSClient(sid_responses={"22331D": ['0462331D00AAAAAA']})
    assert client.read_field("7ec.31.62331d") == pytest.approx(0.0)
