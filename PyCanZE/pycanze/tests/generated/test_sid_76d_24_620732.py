from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620732():
    client = ReplayUDSClient(sid_responses={"220732": ['0462073201000000']})
    assert client.read_field("76d.24.620732") == pytest.approx(0.1)
