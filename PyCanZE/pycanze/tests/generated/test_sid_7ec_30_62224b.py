from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_62224b():
    client = ReplayUDSClient(sid_responses={"22224B": ['0462224B00AAAAAA']})
    assert client.read_field("7ec.30.62224b") == pytest.approx(0.0)
