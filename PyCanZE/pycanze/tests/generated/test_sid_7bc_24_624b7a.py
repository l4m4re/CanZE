from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b7a():
    client = ReplayUDSClient(sid_responses={"224B7A": ['04624B7A5D000000']})
    assert client.read_field("7bc.24.624b7a") == pytest.approx(3.2)
