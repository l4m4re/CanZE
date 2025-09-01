from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b74():
    client = ReplayUDSClient(sid_responses={"224B74": ['04624B747E000000']})
    assert client.read_field("7bc.24.624b74") == pytest.approx(-0.2)
