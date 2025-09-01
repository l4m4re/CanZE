from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_48_622009():
    client = ReplayUDSClient(sid_responses={"222009": ['100A6220090B0C0E', '21111317000B0C0E']})
    assert client.read_field("76e.48.622009") == pytest.approx(17.0)
