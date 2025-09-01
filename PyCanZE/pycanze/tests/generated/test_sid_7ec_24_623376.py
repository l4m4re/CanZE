from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623376():
    client = ReplayUDSClient(sid_responses={"223376": ['05623376003EAAAA']})
    assert client.read_field("7ec.24.623376") == pytest.approx(6.2)
