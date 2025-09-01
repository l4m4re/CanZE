from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62350f():
    client = ReplayUDSClient(sid_responses={"22350F": ['0462350F00AAAAAA']})
    assert client.read_field("7ec.24.62350f") == pytest.approx(0.0)
