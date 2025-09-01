from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b84():
    client = ReplayUDSClient(sid_responses={"224B84": ['04624B8400000000']})
    assert client.read_field("7bc.24.624b84") == pytest.approx(0.0)
