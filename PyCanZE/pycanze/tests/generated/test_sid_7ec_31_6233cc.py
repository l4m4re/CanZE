from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6233cc():
    client = ReplayUDSClient(sid_responses={"2233CC": ['046233CC00AAAAAA']})
    assert client.read_field("7ec.31.6233cc") == pytest.approx(0.0)
