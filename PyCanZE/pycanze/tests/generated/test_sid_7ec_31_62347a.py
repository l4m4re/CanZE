from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62347a():
    client = ReplayUDSClient(sid_responses={"22347A": ['0462347A00AAAAAA']})
    assert client.read_field("7ec.31.62347a") == pytest.approx(0.0)
