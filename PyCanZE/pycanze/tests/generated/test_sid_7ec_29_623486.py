from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_623486():
    client = ReplayUDSClient(sid_responses={"223486": ['0462348600AAAAAA']})
    assert client.read_field("7ec.29.623486") == pytest.approx(0.0)
