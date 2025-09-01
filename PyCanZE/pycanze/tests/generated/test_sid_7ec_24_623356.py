from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623356():
    client = ReplayUDSClient(sid_responses={"223356": ['0762335600FE290E']})
    assert client.read_field("7ec.24.623356") == pytest.approx(16656654.0)
