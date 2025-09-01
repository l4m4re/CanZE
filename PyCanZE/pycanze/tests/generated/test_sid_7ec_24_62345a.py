from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62345a():
    client = ReplayUDSClient(sid_responses={"22345A": ['0462345A00AAAAAA']})
    assert client.read_field("7ec.24.62345a") == pytest.approx(0.0)
