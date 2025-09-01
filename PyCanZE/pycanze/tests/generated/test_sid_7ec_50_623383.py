from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_50_623383():
    client = ReplayUDSClient(sid_responses={"223383": ['1008623383000000', '210000AAAAAAAAAA']})
    assert client.read_field("7ec.50.623383") == pytest.approx(0.0)
