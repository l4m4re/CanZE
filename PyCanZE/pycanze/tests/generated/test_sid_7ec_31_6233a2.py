from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6233a2():
    client = ReplayUDSClient(sid_responses={"2233A2": ['046233A200AAAAAA']})
    assert client.read_field("7ec.31.6233a2") == pytest.approx(0.0)
