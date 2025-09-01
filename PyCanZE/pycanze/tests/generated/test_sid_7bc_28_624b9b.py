from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_28_624b9b():
    client = ReplayUDSClient(sid_responses={"224B9B": ['07624B9B004799E4']})
    assert client.read_field("7bc.28.624b9b") == pytest.approx(46924520.0)
