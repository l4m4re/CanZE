from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_40_62200a():
    client = ReplayUDSClient(sid_responses={"22200A": ['0762200A02030205']})
    assert client.read_field("76e.40.62200a") == pytest.approx(2.0)
