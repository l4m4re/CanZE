from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620730():
    client = ReplayUDSClient(sid_responses={"220730": ['0462073005000000']})
    assert client.read_field("76d.24.620730") == pytest.approx(200.0)
