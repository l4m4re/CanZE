from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623331():
    client = ReplayUDSClient(sid_responses={"223331": ['0462333100AAAAAA']})
    assert client.read_field("7ec.30.623331") == pytest.approx(0.0)
