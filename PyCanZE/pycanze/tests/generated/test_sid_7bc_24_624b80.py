from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b80():
    client = ReplayUDSClient(sid_responses={"224B80": ['04624B8000000000']})
    assert client.read_field("7bc.24.624b80") == pytest.approx(0.0)
