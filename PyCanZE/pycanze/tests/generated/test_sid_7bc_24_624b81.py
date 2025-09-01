from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b81():
    client = ReplayUDSClient(sid_responses={"224B81": ['04624B8100000000']})
    assert client.read_field("7bc.24.624b81") == pytest.approx(0.0)
