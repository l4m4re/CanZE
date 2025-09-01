from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6234c7():
    client = ReplayUDSClient(sid_responses={"2234C7": ['046234C701AAAAAA']})
    assert client.read_field("7ec.30.6234c7") == pytest.approx(1.0)
