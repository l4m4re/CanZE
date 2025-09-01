from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207a3():
    client = ReplayUDSClient(sid_responses={"2207A3": ['046207A301000000']})
    assert client.read_field("76d.24.6207a3") == pytest.approx(1.0)
