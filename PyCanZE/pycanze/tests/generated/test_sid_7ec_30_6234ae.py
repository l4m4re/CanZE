from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6234ae():
    client = ReplayUDSClient(sid_responses={"2234AE": ['046234AE00AAAAAA']})
    assert client.read_field("7ec.30.6234ae") == pytest.approx(0.0)
