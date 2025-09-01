from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6233f4():
    client = ReplayUDSClient(sid_responses={"2233F4": ['056233F41F37AAAA']})
    assert client.read_field("7ec.24.6233f4") == pytest.approx(-224.9)
