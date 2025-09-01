from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623493():
    client = ReplayUDSClient(sid_responses={"223493": ['0462349300AAAAAA']})
    assert client.read_field("7ec.31.623493") == pytest.approx(0.0)
