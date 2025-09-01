from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6233ac():
    client = ReplayUDSClient(sid_responses={"2233AC": ['046233AC00AAAAAA']})
    assert client.read_field("7ec.30.6233ac") == pytest.approx(0.0)
