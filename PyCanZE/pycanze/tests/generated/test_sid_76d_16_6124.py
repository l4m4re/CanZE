from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_16_6124():
    client = ReplayUDSClient(sid_responses={"2124": ['0361240000000000']})
    assert client.read_field("76d.16.6124") == pytest.approx(0.0)
