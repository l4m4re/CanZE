from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6233b5():
    client = ReplayUDSClient(sid_responses={"2233B5": ['046233B500AAAAAA']})
    assert client.read_field("7ec.31.6233b5") == pytest.approx(0.0)
