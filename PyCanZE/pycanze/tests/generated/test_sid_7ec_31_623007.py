from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623007():
    client = ReplayUDSClient(sid_responses={"223007": ['0462300700AAAAAA']})
    assert client.read_field("7ec.31.623007") == pytest.approx(0.0)
