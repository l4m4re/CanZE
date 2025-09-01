from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62347b():
    client = ReplayUDSClient(sid_responses={"22347B": ['0462347B00AAAAAA']})
    assert client.read_field("7ec.31.62347b") == pytest.approx(0.0)
