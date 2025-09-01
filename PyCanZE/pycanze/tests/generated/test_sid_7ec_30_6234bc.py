from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6234bc():
    client = ReplayUDSClient(sid_responses={"2234BC": ['046234BC01AAAAAA']})
    assert client.read_field("7ec.30.6234bc") == pytest.approx(1.0)
