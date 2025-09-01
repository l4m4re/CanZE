from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_136_61ff():
    client = ReplayUDSClient(sid_responses={"21FF": ['101A61FF34343333', '2152504C414E5445', '22434F535F011804', '232708315CBD10AA']})
    assert client.read_field("7ec.136.61ff") == pytest.approx(1.0)
