from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234ef():
    client = ReplayUDSClient(sid_responses={"2234EF": ['046234EF41AAAAAA']})
    assert client.read_field("7ec.24.6234ef") == pytest.approx(25.0)
