from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b9b():
    client = ReplayUDSClient(sid_responses={"224B9B": ['07624B9B004799E4']})
    assert client.read_field("7bc.24.624b9b") == pytest.approx(0.0)
