from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_620100():
    client = ReplayUDSClient(sid_responses={"220100": ['0562010079020000']})
    assert client.read_field("7bc.24.620100") == pytest.approx(-178.9)
