from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620710():
    client = ReplayUDSClient(sid_responses={"220710": ['0462071000000000']})
    assert client.read_field("76d.24.620710") == pytest.approx(0.16)
