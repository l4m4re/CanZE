from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_622039():
    client = ReplayUDSClient(sid_responses={"222039": ['056220390F9AAAAA']})
    assert client.read_field("7ec.24.622039") == pytest.approx(3994.0)
