from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b85():
    client = ReplayUDSClient(sid_responses={"224B85": ['04624B8500000000']})
    assert client.read_field("7bc.24.624b85") == pytest.approx(0.0)
