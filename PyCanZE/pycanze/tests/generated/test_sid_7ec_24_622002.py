from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_622002():
    client = ReplayUDSClient(sid_responses={"222002": ['0562200208F5AAAA']})
    assert client.read_field("7ec.24.622002") == pytest.approx(45.86)
