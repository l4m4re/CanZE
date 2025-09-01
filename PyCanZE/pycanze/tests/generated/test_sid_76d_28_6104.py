from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_28_6104():
    client = ReplayUDSClient(sid_responses={"2104": ['0761048020200000']})
    assert client.read_field("76d.28.6104") == pytest.approx(0.0)
