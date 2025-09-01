from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62344f():
    client = ReplayUDSClient(sid_responses={"22344F": ['0462344F00AAAAAA']})
    assert client.read_field("7ec.31.62344f") == pytest.approx(0.0)
