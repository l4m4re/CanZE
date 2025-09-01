from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_24_622011():
    client = ReplayUDSClient(sid_responses={"222011": ['0462201105000C0E']})
    assert client.read_field("76e.24.622011") == pytest.approx(5.0)
