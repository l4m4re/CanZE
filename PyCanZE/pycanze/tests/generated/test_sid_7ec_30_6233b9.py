from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6233b9():
    client = ReplayUDSClient(sid_responses={"2233B9": ['046233B901AAAAAA']})
    assert client.read_field("7ec.30.6233b9") == pytest.approx(1.0)
