from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623023():
    client = ReplayUDSClient(sid_responses={"223023": ['046230231EAAAAAA']})
    assert client.read_field("7ec.24.623023") == pytest.approx(13.5)
