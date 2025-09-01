from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623359():
    client = ReplayUDSClient(sid_responses={"223359": ['0762335900004093']})
    assert client.read_field("7ec.24.623359") == pytest.approx(16531.0)
