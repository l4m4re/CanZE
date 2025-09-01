from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620734():
    client = ReplayUDSClient(sid_responses={"220734": ['0462073414000000']})
    assert client.read_field("76d.24.620734") == pytest.approx(2.0)
