from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623363():
    client = ReplayUDSClient(sid_responses={"223363": ['0762336300006104']})
    assert client.read_field("7ec.24.623363") == pytest.approx(24836.0)
