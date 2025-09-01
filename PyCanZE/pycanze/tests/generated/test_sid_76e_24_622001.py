from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_24_622001():
    client = ReplayUDSClient(sid_responses={"222001": ['0462200100302020']})
    assert client.read_field("76e.24.622001") == pytest.approx(0.0)
