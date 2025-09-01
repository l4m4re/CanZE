from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62344c():
    client = ReplayUDSClient(sid_responses={"22344C": ['0462344C00AAAAAA']})
    assert client.read_field("7ec.31.62344c") == pytest.approx(0.0)
