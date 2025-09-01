from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_17_6110():
    client = ReplayUDSClient(sid_responses={"2110": ['100F611081E50000', '2100630000000000', '2200000000000000']})
    assert client.read_field("76d.17.6110") == pytest.approx(0.0)
