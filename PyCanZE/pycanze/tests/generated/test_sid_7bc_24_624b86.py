from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b86():
    client = ReplayUDSClient(sid_responses={"224B86": ['04624B86AA000000']})
    assert client.read_field("7bc.24.624b86") == pytest.approx(170.0)
