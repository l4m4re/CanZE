from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62330a():
    client = ReplayUDSClient(sid_responses={"22330A": ['0462330A00AAAAAA']})
    assert client.read_field("7ec.31.62330a") == pytest.approx(0.0)
