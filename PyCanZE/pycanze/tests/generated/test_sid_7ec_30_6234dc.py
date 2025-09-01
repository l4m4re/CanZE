from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6234dc():
    client = ReplayUDSClient(sid_responses={"2234DC": ['046234DC00AAAAAA']})
    assert client.read_field("7ec.30.6234dc") == pytest.approx(0.0)
