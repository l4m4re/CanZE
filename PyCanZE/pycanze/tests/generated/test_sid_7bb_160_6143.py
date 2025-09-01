from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bb_160_6143():
    client = ReplayUDSClient(sid_responses={"2143": ['1032614300070004', '2100060006000600', '2206000400040006', '23000400060000FF', '24FFFFFFFFFFFFFF', '25FFFFFFFFFFFFFF', '26FFFFFFFFFFFFFF', '27FFFF0000000000']})
    assert client.read_field("7bb.160.6143") == pytest.approx(0.004)
