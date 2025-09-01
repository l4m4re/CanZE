from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6233f0():
    client = ReplayUDSClient(sid_responses={"2233F0": ['046233F000AAAAAA']})
    assert client.read_field("7ec.30.6233f0") == pytest.approx(0.0)
