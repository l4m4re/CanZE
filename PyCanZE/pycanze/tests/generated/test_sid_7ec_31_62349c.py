from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62349c():
    client = ReplayUDSClient(sid_responses={"22349C": ['0462349C00AAAAAA']})
    assert client.read_field("7ec.31.62349c") == pytest.approx(0.0)
