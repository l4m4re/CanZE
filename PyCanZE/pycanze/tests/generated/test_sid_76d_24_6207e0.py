from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207e0():
    client = ReplayUDSClient(sid_responses={"2207E0": ['046207E000000000']})
    assert client.read_field("76d.24.6207e0") == pytest.approx(0.0)
