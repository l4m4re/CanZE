from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62344a():
    client = ReplayUDSClient(sid_responses={"22344A": ['0462344A00AAAAAA']})
    assert client.read_field("7ec.24.62344a") == pytest.approx(0.0)
