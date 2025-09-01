from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6233cf():
    client = ReplayUDSClient(sid_responses={"2233CF": ['046233CF00AAAAAA']})
    assert client.read_field("7ec.31.6233cf") == pytest.approx(0.0)
