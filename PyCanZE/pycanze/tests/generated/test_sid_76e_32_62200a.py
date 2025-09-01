from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_32_62200a():
    client = ReplayUDSClient(sid_responses={"22200A": ['0762200A02030205']})
    assert client.read_field("76e.32.62200a") == pytest.approx(3.0)
