from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6233f2():
    client = ReplayUDSClient(sid_responses={"2233F2": ['046233F228AAAAAA']})
    assert client.read_field("7ec.24.6233f2") == pytest.approx(0.0)
