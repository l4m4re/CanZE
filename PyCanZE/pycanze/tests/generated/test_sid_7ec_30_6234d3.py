from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6234d3():
    client = ReplayUDSClient(sid_responses={"2234D3": ['046234D300AAAAAA']})
    assert client.read_field("7ec.30.6234d3") == pytest.approx(0.0)
