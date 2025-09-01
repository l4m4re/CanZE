from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6233fa():
    client = ReplayUDSClient(sid_responses={"2233FA": ['046233FA00AAAAAA']})
    assert client.read_field("7ec.31.6233fa") == pytest.approx(0.0)
