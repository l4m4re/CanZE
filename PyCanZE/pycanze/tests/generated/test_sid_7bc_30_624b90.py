from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_30_624b90():
    client = ReplayUDSClient(sid_responses={"224B90": ['05624B9089800000']})
    assert client.read_field("7bc.30.624b90") == pytest.approx(0.0)
