from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_24_62200e():
    client = ReplayUDSClient(sid_responses={"22200E": ['0462200E000B0C0E']})
    assert client.read_field("76e.24.62200e") == pytest.approx(0.0)
