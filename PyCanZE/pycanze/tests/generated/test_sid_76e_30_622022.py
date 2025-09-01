from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_30_622022():
    client = ReplayUDSClient(sid_responses={"222022": ['04622022081E643C']})
    assert client.read_field("76e.30.622022") == pytest.approx(0.0)
