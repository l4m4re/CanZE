from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62338a():
    client = ReplayUDSClient(sid_responses={"22338A": ['0462338A00AAAAAA']})
    assert client.read_field("7ec.31.62338a") == pytest.approx(0.0)
