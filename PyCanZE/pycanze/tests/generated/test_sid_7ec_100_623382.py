from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_100_623382():
    client = ReplayUDSClient(sid_responses={"223382": ['100D623382002200', '2122002200220022']})
    assert client.read_field("7ec.100.623382") == pytest.approx(0.0)
