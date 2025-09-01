from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b72():
    client = ReplayUDSClient(sid_responses={"224B72": ['04624B727D000000']})
    assert client.read_field("7bc.24.624b72") == pytest.approx(-0.4)
