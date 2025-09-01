from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_30_6101():
    client = ReplayUDSClient(sid_responses={"2101": ['0461010401000000']})
    assert client.read_field("76d.30.6101") == pytest.approx(0.0)
