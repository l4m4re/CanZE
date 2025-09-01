from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_27_62204f():
    client = ReplayUDSClient(sid_responses={"22204F": ['0462204FA4AAAAAA']})
    assert client.read_field("7ec.27.62204f") == pytest.approx(0.0)
