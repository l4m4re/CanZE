from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62200b():
    client = ReplayUDSClient(sid_responses={"22200B": ['0562200B02EBAAAA']})
    assert client.read_field("7ec.24.62200b") == pytest.approx(747.0)
