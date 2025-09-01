from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_622223():
    client = ReplayUDSClient(sid_responses={"222223": ['0462222300AAAAAA']})
    assert client.read_field("7ec.31.622223") == pytest.approx(0.0)
