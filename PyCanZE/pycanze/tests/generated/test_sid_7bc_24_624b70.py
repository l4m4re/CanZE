from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b70():
    client = ReplayUDSClient(sid_responses={"224B70": ['04624B7000000000']})
    assert client.read_field("7bc.24.624b70") == pytest.approx(0.0)
