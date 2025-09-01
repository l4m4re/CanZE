from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620766():
    client = ReplayUDSClient(sid_responses={"220766": ['0462076600000000']})
    assert client.read_field("76d.24.620766") == pytest.approx(0.0)
