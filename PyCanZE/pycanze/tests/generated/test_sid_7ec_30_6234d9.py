from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6234d9():
    client = ReplayUDSClient(sid_responses={"2234D9": ['046234D900AAAAAA']})
    assert client.read_field("7ec.30.6234d9") == pytest.approx(0.0)
