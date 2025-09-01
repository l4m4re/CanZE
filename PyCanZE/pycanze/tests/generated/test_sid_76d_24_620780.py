from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620780():
    client = ReplayUDSClient(sid_responses={"220780": ['0462078001000000']})
    assert client.read_field("76d.24.620780") == pytest.approx(0.0)
