from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_77e_31_622077():
    client = ReplayUDSClient(sid_responses={"222077": ['0462207700AAAAAA']})
    assert client.read_field("77e.31.622077") == pytest.approx(0.0)
