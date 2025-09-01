from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623025():
    client = ReplayUDSClient(sid_responses={"223025": ['04623025FEAAAAAA']})
    assert client.read_field("7ec.24.623025") == pytest.approx(254.0)
