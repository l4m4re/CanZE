from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620720():
    client = ReplayUDSClient(sid_responses={"220720": ['046207205A000000']})
    assert client.read_field("76d.24.620720") == pytest.approx(45.0)
