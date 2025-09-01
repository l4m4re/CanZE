from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b73():
    client = ReplayUDSClient(sid_responses={"224B73": ['04624B7300000000']})
    assert client.read_field("7bc.24.624b73") == pytest.approx(0.0)
