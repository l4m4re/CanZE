from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6234d4():
    client = ReplayUDSClient(sid_responses={"2234D4": ['046234D401AAAAAA']})
    assert client.read_field("7ec.30.6234d4") == pytest.approx(1.0)
