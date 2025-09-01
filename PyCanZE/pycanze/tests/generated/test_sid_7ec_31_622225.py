from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_622225():
    client = ReplayUDSClient(sid_responses={"222225": ['0462222500AAAAAA']})
    assert client.read_field("7ec.31.622225") == pytest.approx(0.0)
