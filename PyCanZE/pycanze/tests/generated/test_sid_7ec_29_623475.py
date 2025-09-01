from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_623475():
    client = ReplayUDSClient(sid_responses={"223475": ['0462347501AAAAAA']})
    assert client.read_field("7ec.29.623475") == pytest.approx(1.0)
