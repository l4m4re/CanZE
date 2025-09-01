from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_6233ab():
    client = ReplayUDSClient(sid_responses={"2233AB": ['046233AB00AAAAAA']})
    assert client.read_field("7ec.29.6233ab") == pytest.approx(0.0)
