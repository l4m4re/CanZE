from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_28_624b7d():
    client = ReplayUDSClient(sid_responses={"224B7D": ['05624B7D0FFE0000']})
    assert client.read_field("7bc.28.624b7d") == pytest.approx(0.0)
