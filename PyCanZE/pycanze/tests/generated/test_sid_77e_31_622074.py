from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_77e_31_622074():
    client = ReplayUDSClient(sid_responses={"222074": ['0462207400AAAAAA']})
    assert client.read_field("77e.31.622074") == pytest.approx(0.0)
