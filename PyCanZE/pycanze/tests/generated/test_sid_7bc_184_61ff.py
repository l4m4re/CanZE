from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_184_61ff():
    client = ReplayUDSClient(sid_responses={"21FF": ['101A61FF30303030', '2130504C414E5445', '22434F535F021804', '232708325C98AA00']})
    assert client.read_field("7bc.184.61ff") == pytest.approx(92.0)
