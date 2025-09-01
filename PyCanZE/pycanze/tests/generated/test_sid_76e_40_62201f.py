from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_40_62201f():
    client = ReplayUDSClient(sid_responses={"22201F": ['100862201F1E643C', '21643C201F1E643C']})
    assert client.read_field("76e.40.62201f") == pytest.approx(60.0)
