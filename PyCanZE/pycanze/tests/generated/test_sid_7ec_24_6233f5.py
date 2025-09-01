from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6233f5():
    client = ReplayUDSClient(sid_responses={"2233F5": ['046233F528AAAAAA']})
    assert client.read_field("7ec.24.6233f5") == pytest.approx(0.0)
