from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_28_624b9d():
    client = ReplayUDSClient(sid_responses={"224B9D": ['05624B9D0FFE0000']})
    assert client.read_field("7bc.28.624b9d") == pytest.approx(0.0)
