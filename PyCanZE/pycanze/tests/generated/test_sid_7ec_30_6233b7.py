from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6233b7():
    client = ReplayUDSClient(sid_responses={"2233B7": ['046233B700AAAAAA']})
    assert client.read_field("7ec.30.6233b7") == pytest.approx(0.0)
