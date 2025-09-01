from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623309():
    client = ReplayUDSClient(sid_responses={"223309": ['0462330900AAAAAA']})
    assert client.read_field("7ec.31.623309") == pytest.approx(0.0)
