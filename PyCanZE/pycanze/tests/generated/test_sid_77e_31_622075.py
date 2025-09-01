from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_77e_31_622075():
    client = ReplayUDSClient(sid_responses={"222075": ['0462207500AAAAAA']})
    assert client.read_field("77e.31.622075") == pytest.approx(0.0)
