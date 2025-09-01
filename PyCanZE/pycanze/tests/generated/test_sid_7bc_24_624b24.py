from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b24():
    client = ReplayUDSClient(sid_responses={"224B24": ['05624B2407670000']})
    assert client.read_field("7bc.24.624b24") == pytest.approx(1895.0)
