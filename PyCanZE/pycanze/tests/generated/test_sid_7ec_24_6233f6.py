from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6233f6():
    client = ReplayUDSClient(sid_responses={"2233F6": ['046233F628AAAAAA']})
    assert client.read_field("7ec.24.6233f6") == pytest.approx(0.0)
