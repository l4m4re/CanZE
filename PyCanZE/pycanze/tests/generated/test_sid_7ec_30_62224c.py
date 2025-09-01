from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_62224c():
    client = ReplayUDSClient(sid_responses={"22224C": ['0462224C01AAAAAA']})
    assert client.read_field("7ec.30.62224c") == pytest.approx(1.0)
