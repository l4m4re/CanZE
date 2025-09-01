from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6233a4():
    client = ReplayUDSClient(sid_responses={"2233A4": ['046233A400AAAAAA']})
    assert client.read_field("7ec.24.6233a4") == pytest.approx(0.0)
