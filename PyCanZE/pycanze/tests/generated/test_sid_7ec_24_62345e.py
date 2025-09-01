from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62345e():
    client = ReplayUDSClient(sid_responses={"22345E": ['0462345E05AAAAAA']})
    assert client.read_field("7ec.24.62345e") == pytest.approx(5.0)
