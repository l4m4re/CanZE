from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_622006():
    client = ReplayUDSClient(sid_responses={"222006": ['0662200600B74DAA']})
    assert client.read_field("7ec.24.622006") == pytest.approx(46925.0)
