from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623487():
    client = ReplayUDSClient(sid_responses={"223487": ['07623487000C44DF']})
    assert client.read_field("7ec.24.623487") == pytest.approx(804063.0)
