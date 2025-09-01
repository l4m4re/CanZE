from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b75():
    client = ReplayUDSClient(sid_responses={"224B75": ['04624B75A0000000']})
    assert client.read_field("7bc.24.624b75") == pytest.approx(160.0)
