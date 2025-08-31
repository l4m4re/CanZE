from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623318():
    client = ReplayUDSClient(sid_responses={"223318": ['0462331814AAAAAA']})
    assert client.read_field("7ec.24.623318") == pytest.approx(19.0)
