from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_32_622017():
    client = ReplayUDSClient(sid_responses={"222017": ['076220172B300000']})
    assert client.read_field("76e.32.622017") == pytest.approx(48.0)
