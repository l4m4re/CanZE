from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_62345f():
    client = ReplayUDSClient(sid_responses={"22345F": ['0562345F0000AAAA']})
    assert client.read_field("7ec.29.62345f") == pytest.approx(0.0)
