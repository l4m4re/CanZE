from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_24_624b36():
    client = ReplayUDSClient(sid_responses={"224B36": ['04624B3677000000']})
    assert client.read_field("7bc.24.624b36") == pytest.approx(-1.6)
