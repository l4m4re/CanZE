from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_6233f8():
    client = ReplayUDSClient(sid_responses={"2233F8": ['046233F800AAAAAA']})
    assert client.read_field("7ec.29.6233f8") == pytest.approx(0.0)
