from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62203c():
    client = ReplayUDSClient(sid_responses={"22203C": ['0462203C00AAAAAA']})
    assert client.read_field("7ec.31.62203c") == pytest.approx(0.0)
