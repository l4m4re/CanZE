from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623313():
    client = ReplayUDSClient(sid_responses={"223313": ['0462331300AAAAAA']})
    assert client.read_field("7ec.31.623313") == pytest.approx(0.0)
