from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620763():
    client = ReplayUDSClient(sid_responses={"220763": ['0462076300000000']})
    assert client.read_field("76d.24.620763") == pytest.approx(0.0)
