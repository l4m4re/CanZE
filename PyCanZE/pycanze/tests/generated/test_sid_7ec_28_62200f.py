from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_28_62200f():
    client = ReplayUDSClient(sid_responses={"22200F": ['0462200F02AAAAAA']})
    assert client.read_field("7ec.28.62200f") == pytest.approx(2.0)
