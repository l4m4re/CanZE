from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b95():
    client = ReplayUDSClient(sid_responses={"224B95": ['04624B9500000000']})
    assert client.read_field("7bc.24.624b95") == pytest.approx(0.0)
