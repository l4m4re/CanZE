from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62350e():
    client = ReplayUDSClient(sid_responses={"22350E": ['0562350E2328AAAA']})
    assert client.read_field("7ec.24.62350e") == pytest.approx(9000.0)
