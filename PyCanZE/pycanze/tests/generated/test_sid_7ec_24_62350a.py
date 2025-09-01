from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62350a():
    client = ReplayUDSClient(sid_responses={"22350A": ['0462350A00AAAAAA']})
    assert client.read_field("7ec.24.62350a") == pytest.approx(0.0)
