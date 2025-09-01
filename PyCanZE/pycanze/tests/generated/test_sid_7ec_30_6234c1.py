from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6234c1():
    client = ReplayUDSClient(sid_responses={"2234C1": ['046234C100AAAAAA']})
    assert client.read_field("7ec.30.6234c1") == pytest.approx(0.0)
