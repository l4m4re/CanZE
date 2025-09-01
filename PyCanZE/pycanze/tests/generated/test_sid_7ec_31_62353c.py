from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62353c():
    client = ReplayUDSClient(sid_responses={"22353C": ['0462353C00AAAAAA']})
    assert client.read_field("7ec.31.62353c") == pytest.approx(0.0)
