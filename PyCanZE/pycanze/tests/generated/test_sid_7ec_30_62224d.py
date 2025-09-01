from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_62224d():
    client = ReplayUDSClient(sid_responses={"22224D": ['0462224D01AAAAAA']})
    assert client.read_field("7ec.30.62224d") == pytest.approx(1.0)
