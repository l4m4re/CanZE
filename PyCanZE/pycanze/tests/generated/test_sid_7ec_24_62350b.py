from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62350b():
    client = ReplayUDSClient(sid_responses={"22350B": ['0462350B01AAAAAA']})
    assert client.read_field("7ec.24.62350b") == pytest.approx(1.0)
