from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_136_61f1():
    client = ReplayUDSClient(sid_responses={"21F1": ['101A61F100000000', '2100F000000000F0', '2200000000001406', '232700005CAB3700']})
    assert client.read_field("7bc.136.61f1") == pytest.approx(0.0)
