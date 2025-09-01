from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620764():
    client = ReplayUDSClient(sid_responses={"220764": ['0462076400000000']})
    assert client.read_field("76d.24.620764") == pytest.approx(0.0)
