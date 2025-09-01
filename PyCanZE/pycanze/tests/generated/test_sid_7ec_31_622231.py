from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_622231():
    client = ReplayUDSClient(sid_responses={"222231": ['0462223100AAAAAA']})
    assert client.read_field("7ec.31.622231") == pytest.approx(0.0)
