from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623379():
    client = ReplayUDSClient(sid_responses={"223379": ['0462337900AAAAAA']})
    assert client.read_field("7ec.30.623379") == pytest.approx(0.0)
