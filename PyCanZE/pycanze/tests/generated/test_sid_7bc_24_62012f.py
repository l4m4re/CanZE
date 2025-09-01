from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_62012f():
    client = ReplayUDSClient(sid_responses={"22012F": ['0462012F86000000']})
    assert client.read_field("7bc.24.62012f") == pytest.approx(13.4)
