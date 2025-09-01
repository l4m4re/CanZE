from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_622249():
    client = ReplayUDSClient(sid_responses={"222249": ['0562224985A0AAAA']})
    assert client.read_field("7ec.24.622249") == pytest.approx(720.0)
