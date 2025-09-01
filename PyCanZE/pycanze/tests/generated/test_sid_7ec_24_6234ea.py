from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234ea():
    client = ReplayUDSClient(sid_responses={"2234EA": ['046234EA64AAAAAA']})
    assert client.read_field("7ec.24.6234ea") == pytest.approx(20.0)
