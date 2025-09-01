from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_622233():
    client = ReplayUDSClient(sid_responses={"222233": ['0462223300AAAAAA']})
    assert client.read_field("7ec.31.622233") == pytest.approx(0.0)
