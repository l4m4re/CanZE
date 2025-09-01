from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bb_144_61ff():
    client = ReplayUDSClient(sid_responses={"21FF": ['101A61FF00000000', '21004B4F5245414C', '2247454F4C000000', '230000005CD0A200']})
    assert client.read_field("7bb.144.61ff") == pytest.approx(0.0)
