from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623395():
    client = ReplayUDSClient(sid_responses={"223395": ['0462339500AAAAAA']})
    assert client.read_field("7ec.31.623395") == pytest.approx(0.0)
