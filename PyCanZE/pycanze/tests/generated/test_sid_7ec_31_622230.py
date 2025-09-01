from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_622230():
    client = ReplayUDSClient(sid_responses={"222230": ['0462223000AAAAAA']})
    assert client.read_field("7ec.31.622230") == pytest.approx(0.0)
