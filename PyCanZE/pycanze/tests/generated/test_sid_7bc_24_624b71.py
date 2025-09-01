from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b71():
    client = ReplayUDSClient(sid_responses={"224B71": ['04624B7100000000']})
    assert client.read_field("7bc.24.624b71") == pytest.approx(0.0)
