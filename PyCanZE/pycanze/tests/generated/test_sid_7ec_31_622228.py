from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_622228():
    client = ReplayUDSClient(sid_responses={"222228": ['0462222800AAAAAA']})
    assert client.read_field("7ec.31.622228") == pytest.approx(0.0)
