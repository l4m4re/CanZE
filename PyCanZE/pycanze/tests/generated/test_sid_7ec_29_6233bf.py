from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_6233bf():
    client = ReplayUDSClient(sid_responses={"2233BF": ['046233BF01AAAAAA']})
    assert client.read_field("7ec.29.6233bf") == pytest.approx(1.0)
