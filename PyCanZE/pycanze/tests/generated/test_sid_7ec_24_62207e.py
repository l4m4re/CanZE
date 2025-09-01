from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62207e():
    client = ReplayUDSClient(sid_responses={"22207E": ['0462207E01AAAAAA']})
    assert client.read_field("7ec.24.62207e") == pytest.approx(1.0)
