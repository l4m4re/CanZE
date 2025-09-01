from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_622026():
    client = ReplayUDSClient(sid_responses={"222026": ['0462202602AAAAAA']})
    assert client.read_field("7ec.30.622026") == pytest.approx(2.0)
