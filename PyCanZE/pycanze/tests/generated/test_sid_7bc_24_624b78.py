from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b78():
    client = ReplayUDSClient(sid_responses={"224B78": ['04624B785D000000']})
    assert client.read_field("7bc.24.624b78") == pytest.approx(3.2)
