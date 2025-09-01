from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62347c():
    client = ReplayUDSClient(sid_responses={"22347C": ['0462347C00AAAAAA']})
    assert client.read_field("7ec.31.62347c") == pytest.approx(0.0)
