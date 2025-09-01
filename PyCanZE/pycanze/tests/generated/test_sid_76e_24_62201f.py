from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_24_62201f():
    client = ReplayUDSClient(sid_responses={"22201F": ['100862201F1E643C', '21643C201F1E643C']})
    assert client.read_field("76e.24.62201f") == pytest.approx(30.0)
