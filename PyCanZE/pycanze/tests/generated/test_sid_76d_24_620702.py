from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620702():
    client = ReplayUDSClient(sid_responses={"220702": ['0462070214000000']})
    assert client.read_field("76d.24.620702") == pytest.approx(0.3)
