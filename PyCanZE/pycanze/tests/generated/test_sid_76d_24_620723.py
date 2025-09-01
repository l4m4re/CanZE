from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620723():
    client = ReplayUDSClient(sid_responses={"220723": ['046207231E000000']})
    assert client.read_field("76d.24.620723") == pytest.approx(10.7)
