from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6233ba():
    client = ReplayUDSClient(sid_responses={"2233BA": ['046233BA00AAAAAA']})
    assert client.read_field("7ec.30.6233ba") == pytest.approx(0.0)
