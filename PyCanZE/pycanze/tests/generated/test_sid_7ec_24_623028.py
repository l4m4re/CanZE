from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623028():
    client = ReplayUDSClient(sid_responses={"223028": ['0462302800AAAAAA']})
    assert client.read_field("7ec.24.623028") == pytest.approx(0.0)
