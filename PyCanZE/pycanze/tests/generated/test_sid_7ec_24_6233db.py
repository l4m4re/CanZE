from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6233db():
    client = ReplayUDSClient(sid_responses={"2233DB": ['056233DB4100AAAA']})
    assert client.read_field("7ec.24.6233db") == pytest.approx(65.0)
