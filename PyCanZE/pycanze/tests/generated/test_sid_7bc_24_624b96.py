from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b96():
    client = ReplayUDSClient(sid_responses={"224B96": ['04624B9600000000']})
    assert client.read_field("7bc.24.624b96") == pytest.approx(0.0)
