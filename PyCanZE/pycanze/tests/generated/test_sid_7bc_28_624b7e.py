from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_28_624b7e():
    client = ReplayUDSClient(sid_responses={"224B7E": ['05624B7E0FFE0000']})
    assert client.read_field("7bc.28.624b7e") == pytest.approx(0.0)
