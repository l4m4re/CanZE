from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b97():
    client = ReplayUDSClient(sid_responses={"224B97": ['04624B97A0000000']})
    assert client.read_field("7bc.24.624b97") == pytest.approx(160.0)
