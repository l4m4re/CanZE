from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_77e_24_622072():
    client = ReplayUDSClient(sid_responses={"222072": ['0462207228AAAAAA']})
    assert client.read_field("77e.24.622072") == pytest.approx(40.0)
