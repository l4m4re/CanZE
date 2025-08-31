from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623206():
    client = ReplayUDSClient(sid_responses={"223206": ['046232067EAAAAAA']})
    assert client.read_field("7ec.24.623206") == pytest.approx(126.0)
