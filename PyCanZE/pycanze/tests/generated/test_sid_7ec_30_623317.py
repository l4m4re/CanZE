from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623317():
    client = ReplayUDSClient(sid_responses={"223317": ['0462331702AAAAAA']})
    assert client.read_field("7ec.30.623317") == pytest.approx(2.0)
