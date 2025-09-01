from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_6233ea():
    client = ReplayUDSClient(sid_responses={"2233EA": ['046233EA02AAAAAA']})
    assert client.read_field("7ec.29.6233ea") == pytest.approx(2.0)
