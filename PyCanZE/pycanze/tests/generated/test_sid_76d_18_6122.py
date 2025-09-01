from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_18_6122():
    client = ReplayUDSClient(sid_responses={"2122": ['100F612208365FEF', '21C00D0043FEA06C', '2280000000000000']})
    assert client.read_field("76d.18.6122") == pytest.approx(0.0)
