from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6234dd():
    client = ReplayUDSClient(sid_responses={"2234DD": ['046234DD01AAAAAA']})
    assert client.read_field("7ec.30.6234dd") == pytest.approx(1.0)
