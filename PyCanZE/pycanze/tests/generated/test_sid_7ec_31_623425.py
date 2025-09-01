from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623425():
    client = ReplayUDSClient(sid_responses={"223425": ['0462342500AAAAAA']})
    assert client.read_field("7ec.31.623425") == pytest.approx(0.0)
