from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207d9():
    client = ReplayUDSClient(sid_responses={"2207D9": ['046207D900000000']})
    assert client.read_field("76d.24.6207d9") == pytest.approx(0.0)
