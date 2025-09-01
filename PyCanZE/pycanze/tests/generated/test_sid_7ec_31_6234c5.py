from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6234c5():
    client = ReplayUDSClient(sid_responses={"2234C5": ['046234C500AAAAAA']})
    assert client.read_field("7ec.31.6234c5") == pytest.approx(0.0)
