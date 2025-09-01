from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623378():
    client = ReplayUDSClient(sid_responses={"223378": ['0462337802AAAAAA']})
    assert client.read_field("7ec.30.623378") == pytest.approx(2.0)
