from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_95_6233d3():
    client = ReplayUDSClient(sid_responses={"2233D3": ['100D6233D3000000', '2100000000000000']})
    assert client.read_field("7ec.95.6233d3") == pytest.approx(0.0)
