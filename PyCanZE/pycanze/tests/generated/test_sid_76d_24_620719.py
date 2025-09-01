from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620719():
    client = ReplayUDSClient(sid_responses={"220719": ['0462071923000000']})
    assert client.read_field("76d.24.620719") == pytest.approx(10.8)
