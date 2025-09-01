from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b1a():
    client = ReplayUDSClient(sid_responses={"224B1A": ['04624B1A04000000']})
    assert client.read_field("7bc.24.624b1a") == pytest.approx(4.0)
