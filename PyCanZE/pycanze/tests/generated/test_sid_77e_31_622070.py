from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_77e_31_622070():
    client = ReplayUDSClient(sid_responses={"222070": ['0462207000AAAAAA']})
    assert client.read_field("77e.31.622070") == pytest.approx(0.0)
