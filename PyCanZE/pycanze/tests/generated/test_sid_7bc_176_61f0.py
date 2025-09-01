from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_176_61f0():
    client = ReplayUDSClient(sid_responses={"21F0": ['101A61F038303531', '2152043033373432', '2235345223960E40', '2300000101008800']})
    assert client.read_field("7bc.176.61f0") == pytest.approx(1.0)
