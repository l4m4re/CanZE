from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b99():
    client = ReplayUDSClient(sid_responses={"224B99": ['04624B9903000000']})
    assert client.read_field("7bc.24.624b99") == pytest.approx(3.0)
