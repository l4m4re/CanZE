from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6233fe():
    client = ReplayUDSClient(sid_responses={"2233FE": ['046233FE00AAAAAA']})
    assert client.read_field("7ec.31.6233fe") == pytest.approx(0.0)
