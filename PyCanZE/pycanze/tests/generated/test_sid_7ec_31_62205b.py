from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62205b():
    client = ReplayUDSClient(sid_responses={"22205B": ['0462205B00AAAAAA']})
    assert client.read_field("7ec.31.62205b") == pytest.approx(0.0)
