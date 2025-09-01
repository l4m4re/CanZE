from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b98():
    client = ReplayUDSClient(sid_responses={"224B98": ['04624B9803000000']})
    assert client.read_field("7bc.24.624b98") == pytest.approx(3.0)
