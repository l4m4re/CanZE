from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6233a3():
    client = ReplayUDSClient(sid_responses={"2233A3": ['046233A300AAAAAA']})
    assert client.read_field("7ec.31.6233a3") == pytest.approx(0.0)
