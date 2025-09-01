from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620753():
    client = ReplayUDSClient(sid_responses={"220753": ['0462075301000000']})
    assert client.read_field("76d.24.620753") == pytest.approx(0.0)
