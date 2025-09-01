from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620761():
    client = ReplayUDSClient(sid_responses={"220761": ['0462076101000000']})
    assert client.read_field("76d.24.620761") == pytest.approx(0.0)
