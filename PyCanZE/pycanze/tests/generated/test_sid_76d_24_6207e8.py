from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207e8():
    client = ReplayUDSClient(sid_responses={"2207E8": ['046207E802000000']})
    assert client.read_field("76d.24.6207e8") == pytest.approx(0.0)
