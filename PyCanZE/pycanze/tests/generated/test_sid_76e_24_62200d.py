from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_24_62200d():
    client = ReplayUDSClient(sid_responses={"22200D": ['0462200D230B0C0E']})
    assert client.read_field("76e.24.62200d") == pytest.approx(35.0)
