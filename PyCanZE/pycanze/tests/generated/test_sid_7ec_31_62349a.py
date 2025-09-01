from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62349a():
    client = ReplayUDSClient(sid_responses={"22349A": ['0462349A00AAAAAA']})
    assert client.read_field("7ec.31.62349a") == pytest.approx(0.0)
