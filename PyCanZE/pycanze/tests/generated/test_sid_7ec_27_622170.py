from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_27_622170():
    client = ReplayUDSClient(sid_responses={"222170": ['0462217000AAAAAA']})
    assert client.read_field("7ec.27.622170") == pytest.approx(0.0)
