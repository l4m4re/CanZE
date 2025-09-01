from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_30_622005():
    client = ReplayUDSClient(sid_responses={"222005": ['056220050532AAAA']})
    assert client.read_field("76e.30.622005") == pytest.approx(0.0)
