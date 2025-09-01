from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207ea():
    client = ReplayUDSClient(sid_responses={"2207EA": ['046207EA00000000']})
    assert client.read_field("76d.24.6207ea") == pytest.approx(0.0)
