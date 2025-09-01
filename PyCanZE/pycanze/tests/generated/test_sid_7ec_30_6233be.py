from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6233be():
    client = ReplayUDSClient(sid_responses={"2233BE": ['046233BE01AAAAAA']})
    assert client.read_field("7ec.30.6233be") == pytest.approx(1.0)
