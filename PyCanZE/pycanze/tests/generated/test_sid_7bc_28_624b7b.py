from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_28_624b7b():
    client = ReplayUDSClient(sid_responses={"224B7B": ['05624B7B0FFE0000']})
    assert client.read_field("7bc.28.624b7b") == pytest.approx(0.0)
