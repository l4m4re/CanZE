from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_623474():
    client = ReplayUDSClient(sid_responses={"223474": ['0462347401AAAAAA']})
    assert client.read_field("7ec.29.623474") == pytest.approx(1.0)
