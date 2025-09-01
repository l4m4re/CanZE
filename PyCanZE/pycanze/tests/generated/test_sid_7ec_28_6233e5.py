from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_28_6233e5():
    client = ReplayUDSClient(sid_responses={"2233E5": ['046233E500AAAAAA']})
    assert client.read_field("7ec.28.6233e5") == pytest.approx(0.0)
