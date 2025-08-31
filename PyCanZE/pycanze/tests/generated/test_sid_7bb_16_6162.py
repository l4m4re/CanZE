from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bb_16_6162():
    client = ReplayUDSClient(sid_responses={"2162": ['0661622604859900']})
    assert client.read_field("7bb.16.6162") == pytest.approx(637830553.0)
