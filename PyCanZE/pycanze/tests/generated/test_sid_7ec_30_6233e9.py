from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6233e9():
    client = ReplayUDSClient(sid_responses={"2233E9": ['046233E900AAAAAA']})
    assert client.read_field("7ec.30.6233e9") == pytest.approx(0.0)
