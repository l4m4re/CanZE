from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6233ca():
    client = ReplayUDSClient(sid_responses={"2233CA": ['046233CA00AAAAAA']})
    assert client.read_field("7ec.31.6233ca") == pytest.approx(0.0)
