from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_25_623326():
    client = ReplayUDSClient(sid_responses={"223326": ['046233260AAAAAAA']})
    assert client.read_field("7ec.25.623326") == pytest.approx(10.0)
