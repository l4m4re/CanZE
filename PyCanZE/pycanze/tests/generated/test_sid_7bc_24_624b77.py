from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b77():
    client = ReplayUDSClient(sid_responses={"224B77": ['04624B7703000000']})
    assert client.read_field("7bc.24.624b77") == pytest.approx(3.0)
