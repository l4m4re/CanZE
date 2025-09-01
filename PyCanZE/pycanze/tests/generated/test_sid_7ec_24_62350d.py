from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62350d():
    client = ReplayUDSClient(sid_responses={"22350D": ['0462350D00AAAAAA']})
    assert client.read_field("7ec.24.62350d") == pytest.approx(0.0)
