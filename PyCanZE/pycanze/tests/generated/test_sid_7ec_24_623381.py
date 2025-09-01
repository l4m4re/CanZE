from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623381():
    client = ReplayUDSClient(sid_responses={"223381": ['0462338100AAAAAA']})
    assert client.read_field("7ec.24.623381") == pytest.approx(0.0)
