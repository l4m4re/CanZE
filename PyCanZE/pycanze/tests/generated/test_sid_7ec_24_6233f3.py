from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6233f3():
    client = ReplayUDSClient(sid_responses={"2233F3": ['056233F330CAAAAA']})
    assert client.read_field("7ec.24.6233f3") == pytest.approx(225.0)
