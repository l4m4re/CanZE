from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6234ba():
    client = ReplayUDSClient(sid_responses={"2234BA": ['046234BA00AAAAAA']})
    assert client.read_field("7ec.30.6234ba") == pytest.approx(0.0)
