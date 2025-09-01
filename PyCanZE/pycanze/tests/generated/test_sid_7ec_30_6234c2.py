from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6234c2():
    client = ReplayUDSClient(sid_responses={"2234C2": ['046234C201AAAAAA']})
    assert client.read_field("7ec.30.6234c2") == pytest.approx(1.0)
