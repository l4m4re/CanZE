from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_24_622008():
    client = ReplayUDSClient(sid_responses={"222008": ['0462200803302020']})
    assert client.read_field("76e.24.622008") == pytest.approx(3.0)
