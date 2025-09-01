from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b79():
    client = ReplayUDSClient(sid_responses={"224B79": ['04624B7903000000']})
    assert client.read_field("7bc.24.624b79") == pytest.approx(3.0)
