from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_62342e():
    client = ReplayUDSClient(sid_responses={"22342E": ['0462342E02AAAAAA']})
    assert client.read_field("7ec.30.62342e") == pytest.approx(2.0)
