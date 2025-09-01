from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_62224e():
    client = ReplayUDSClient(sid_responses={"22224E": ['0462224E01AAAAAA']})
    assert client.read_field("7ec.30.62224e") == pytest.approx(1.0)
