from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bb_192_6180():
    client = ReplayUDSClient(sid_responses={"2180": ['101A618034323539', '21523A3431343030', '22303030C7002460', '2300000100008800']})
    assert client.read_field("7bb.192.6180") == pytest.approx(0.0)
