from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62333d():
    client = ReplayUDSClient(sid_responses={"22333D": ['0462333D00AAAAAA']})
    assert client.read_field("7ec.31.62333d") == pytest.approx(0.0)
