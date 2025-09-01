from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bb_168_61f1():
    client = ReplayUDSClient(sid_responses={"21F1": ['101A61F100000000', '21004B4F5245414C', '2247454F4C000000', '230000005CD0A200']})
    assert client.read_field("7bb.168.61f1") == pytest.approx(0.0)
