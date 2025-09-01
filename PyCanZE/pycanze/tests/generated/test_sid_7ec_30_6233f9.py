from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6233f9():
    client = ReplayUDSClient(sid_responses={"2233F9": ['046233F901AAAAAA']})
    assert client.read_field("7ec.30.6233f9") == pytest.approx(1.0)
