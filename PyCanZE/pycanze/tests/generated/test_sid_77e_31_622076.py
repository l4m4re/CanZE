from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_77e_31_622076():
    client = ReplayUDSClient(sid_responses={"222076": ['0462207600AAAAAA']})
    assert client.read_field("77e.31.622076") == pytest.approx(0.0)
