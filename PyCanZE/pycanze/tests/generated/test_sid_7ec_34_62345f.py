from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_34_62345f():
    client = ReplayUDSClient(sid_responses={"22345F": ['0562345F03DDAAAA']})
    assert client.read_field("7ec.34.62345f") == pytest.approx(0.0)
