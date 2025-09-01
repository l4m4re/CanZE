from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_622051():
    client = ReplayUDSClient(sid_responses={"222051": ['0462205100AAAAAA']})
    assert client.read_field("7ec.31.622051") == pytest.approx(0.0)
