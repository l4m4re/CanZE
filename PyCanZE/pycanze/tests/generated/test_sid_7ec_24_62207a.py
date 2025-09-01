from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62207a():
    client = ReplayUDSClient(sid_responses={"22207A": ['0462207A01AAAAAA']})
    assert client.read_field("7ec.24.62207a") == pytest.approx(1.0)
