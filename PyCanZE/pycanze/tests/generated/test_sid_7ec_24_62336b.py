from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62336b():
    client = ReplayUDSClient(sid_responses={"22336B": ['0462336B4EAAAAAA']})
    assert client.read_field("7ec.24.62336b") == pytest.approx(78.0)
