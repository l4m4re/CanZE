from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207b8():
    client = ReplayUDSClient(sid_responses={"2207B8": ['046207B800000000']})
    assert client.read_field("76d.24.6207b8") == pytest.approx(0.0)
