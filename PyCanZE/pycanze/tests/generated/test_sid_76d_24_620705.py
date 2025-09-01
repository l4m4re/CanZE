from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620705():
    client = ReplayUDSClient(sid_responses={"220705": ['0462070500000000']})
    assert client.read_field("76d.24.620705") == pytest.approx(0.1)
