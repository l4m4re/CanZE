from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6233b3():
    client = ReplayUDSClient(sid_responses={"2233B3": ['046233B349AAAAAA']})
    assert client.read_field("7ec.24.6233b3") == pytest.approx(33.0)
