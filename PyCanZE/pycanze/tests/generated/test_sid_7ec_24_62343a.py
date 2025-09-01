from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62343a():
    client = ReplayUDSClient(sid_responses={"22343A": ['0462343A00AAAAAA']})
    assert client.read_field("7ec.24.62343a") == pytest.approx(0.0)
