from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207cf():
    client = ReplayUDSClient(sid_responses={"2207CF": ['046207CF01000000']})
    assert client.read_field("76d.24.6207cf") == pytest.approx(0.0)
