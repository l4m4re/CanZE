from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_623201():
    client = ReplayUDSClient(sid_responses={"223201": ['0462320100AAAAAA']})
    assert client.read_field("7ec.29.623201") == pytest.approx(0.0)
