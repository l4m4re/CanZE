from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bb_88_6107():
    client = ReplayUDSClient(sid_responses={"2107": ['100E610700000000', '2100000000000000', '2200000000000000']})
    assert client.read_field("7bb.88.6107") == pytest.approx(0.0)
