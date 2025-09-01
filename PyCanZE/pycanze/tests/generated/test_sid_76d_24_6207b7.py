from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207b7():
    client = ReplayUDSClient(sid_responses={"2207B7": ['046207B700000000']})
    assert client.read_field("76d.24.6207b7") == pytest.approx(0.0)
