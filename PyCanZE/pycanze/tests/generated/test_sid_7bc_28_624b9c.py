from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_28_624b9c():
    client = ReplayUDSClient(sid_responses={"224B9C": ['05624B9C0FFE0000']})
    assert client.read_field("7bc.28.624b9c") == pytest.approx(0.0)
