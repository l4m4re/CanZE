from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_184_61fe():
    client = ReplayUDSClient(sid_responses={"21FE": ['101A61FE39393139', '2152043033373432', '2235345223960E40', '2300010201008800']})
    assert client.read_field("7bc.184.61fe") == pytest.approx(1.0)
