from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207cc():
    client = ReplayUDSClient(sid_responses={"2207CC": ['046207CC00000000']})
    assert client.read_field("76d.24.6207cc") == pytest.approx(0.0)
