from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62320a():
    client = ReplayUDSClient(sid_responses={"22320A": ['0462320AC8AAAAAA']})
    assert client.read_field("7ec.24.62320a") == pytest.approx(100.0)
