from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234fa():
    client = ReplayUDSClient(sid_responses={"2234FA": ['046234FA00AAAAAA']})
    assert client.read_field("7ec.24.6234fa") == pytest.approx(0.0)
