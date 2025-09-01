from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_77e_24_622071():
    client = ReplayUDSClient(sid_responses={"222071": ['0462207100AAAAAA']})
    assert client.read_field("77e.24.622071") == pytest.approx(0.0)
