from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62207b():
    client = ReplayUDSClient(sid_responses={"22207B": ['0462207B03AAAAAA']})
    assert client.read_field("7ec.24.62207b") == pytest.approx(3.0)
