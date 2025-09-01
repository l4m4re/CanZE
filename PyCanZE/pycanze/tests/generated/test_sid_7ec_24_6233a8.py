from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6233a8():
    client = ReplayUDSClient(sid_responses={"2233A8": ['046233A800AAAAAA']})
    assert client.read_field("7ec.24.6233a8") == pytest.approx(0.0)
