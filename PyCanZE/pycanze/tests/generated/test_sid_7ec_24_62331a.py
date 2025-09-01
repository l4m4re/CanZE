from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62331a():
    client = ReplayUDSClient(sid_responses={"22331A": ['0462331A00AAAAAA']})
    assert client.read_field("7ec.24.62331a") == pytest.approx(0.0)
