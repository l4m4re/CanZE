from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_622021():
    client = ReplayUDSClient(sid_responses={"222021": ['056220211388AAAA']})
    assert client.read_field("7ec.24.622021") == pytest.approx(5000.0)
