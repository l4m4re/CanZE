from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b9a():
    client = ReplayUDSClient(sid_responses={"224B9A": ['04624B9A00000000']})
    assert client.read_field("7bc.24.624b9a") == pytest.approx(10.0)
