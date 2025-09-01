from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623517():
    client = ReplayUDSClient(sid_responses={"223517": ['0462351704AAAAAA']})
    assert client.read_field("7ec.24.623517") == pytest.approx(4.0)
