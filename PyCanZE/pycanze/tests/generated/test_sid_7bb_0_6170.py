from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bb_0_6170():
    client = ReplayUDSClient(sid_responses={"2170": ['101C6170B82F1847', '210000B600C800AF', '22B9C80006E71160', '2300000000FFFFFF', '24FF000000000000']})
    assert client.read_field("7bb.0.6170") == pytest.approx(0.0)
