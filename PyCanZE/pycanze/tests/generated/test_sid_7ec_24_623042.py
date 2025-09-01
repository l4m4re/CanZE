from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623042():
    client = ReplayUDSClient(sid_responses={"223042": ['056230428320AAAA']})
    assert client.read_field("7ec.24.623042") == pytest.approx(400.0)
