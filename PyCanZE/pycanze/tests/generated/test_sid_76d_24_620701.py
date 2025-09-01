from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620701():
    client = ReplayUDSClient(sid_responses={"220701": ['0462070114000000']})
    assert client.read_field("76d.24.620701") == pytest.approx(0.3)
