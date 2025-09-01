from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207fe():
    client = ReplayUDSClient(sid_responses={"2207FE": ['046207FE00000000']})
    assert client.read_field("76d.24.6207fe") == pytest.approx(0.0)
