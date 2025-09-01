from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_16_6198():
    client = ReplayUDSClient(sid_responses={"2198": ['0461980005000000']})
    assert client.read_field("76d.16.6198") == pytest.approx(5.0)
