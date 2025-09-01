from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6234bb():
    client = ReplayUDSClient(sid_responses={"2234BB": ['046234BB00AAAAAA']})
    assert client.read_field("7ec.30.6234bb") == pytest.approx(0.0)
