from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_28_623522():
    client = ReplayUDSClient(sid_responses={"223522": ['0462352200AAAAAA']})
    assert client.read_field("7ec.28.623522") == pytest.approx(0.0)
