from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6233f1():
    client = ReplayUDSClient(sid_responses={"2233F1": ['056233F11388AAAA']})
    assert client.read_field("7ec.24.6233f1") == pytest.approx(100.0)
