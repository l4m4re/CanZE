from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623494():
    client = ReplayUDSClient(sid_responses={"223494": ['056234940009AAAA']})
    assert client.read_field("7ec.24.623494") == pytest.approx(90.0)
