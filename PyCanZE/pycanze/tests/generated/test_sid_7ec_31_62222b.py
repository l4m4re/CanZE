from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62222b():
    client = ReplayUDSClient(sid_responses={"22222B": ['0462222B00AAAAAA']})
    assert client.read_field("7ec.31.62222b") == pytest.approx(0.0)
