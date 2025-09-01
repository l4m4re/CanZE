from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_77e_24_622073():
    client = ReplayUDSClient(sid_responses={"222073": ['0462207374AAAAAA']})
    assert client.read_field("77e.24.622073") == pytest.approx(116.0)
