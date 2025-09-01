from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620768():
    client = ReplayUDSClient(sid_responses={"220768": ['0462076800000000']})
    assert client.read_field("76d.24.620768") == pytest.approx(0.0)
