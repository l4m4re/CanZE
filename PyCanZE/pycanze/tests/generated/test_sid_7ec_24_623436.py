from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623436():
    client = ReplayUDSClient(sid_responses={"223436": ['056234362328AAAA']})
    assert client.read_field("7ec.24.623436") == pytest.approx(9000.0)
