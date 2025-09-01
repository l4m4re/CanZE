from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_157_6121():
    client = ReplayUDSClient(sid_responses={"2121": ['101F612130C11E67', '2190EF0E5E078000', '2218007F8FF80000', '2300C00740000400', '2400000000000000']})
    assert client.read_field("76d.157.6121") == pytest.approx(-40.0)
