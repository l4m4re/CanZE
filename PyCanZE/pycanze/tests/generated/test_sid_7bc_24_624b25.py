from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b25():
    client = ReplayUDSClient(sid_responses={"224B25": ['04624B2500000000']})
    assert client.read_field("7bc.24.624b25") == pytest.approx(10.0)
