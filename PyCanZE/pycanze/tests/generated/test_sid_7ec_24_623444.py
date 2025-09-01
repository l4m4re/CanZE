from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623444():
    client = ReplayUDSClient(sid_responses={"223444": ['04623444C8AAAAAA']})
    assert client.read_field("7ec.24.623444") == pytest.approx(60.0)
