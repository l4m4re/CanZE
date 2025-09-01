from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207bb():
    client = ReplayUDSClient(sid_responses={"2207BB": ['046207BB32000000']})
    assert client.read_field("76d.24.6207bb") == pytest.approx(10.0)
