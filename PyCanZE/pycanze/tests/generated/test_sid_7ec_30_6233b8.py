from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6233b8():
    client = ReplayUDSClient(sid_responses={"2233B8": ['046233B800AAAAAA']})
    assert client.read_field("7ec.30.6233b8") == pytest.approx(0.0)
