from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_28_623525():
    client = ReplayUDSClient(sid_responses={"223525": ['0462352500AAAAAA']})
    assert client.read_field("7ec.28.623525") == pytest.approx(0.0)
