from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_622184():
    client = ReplayUDSClient(sid_responses={"222184": ['056221844E20AAAA']})
    assert client.read_field("7ec.24.622184") == pytest.approx(200.0)
