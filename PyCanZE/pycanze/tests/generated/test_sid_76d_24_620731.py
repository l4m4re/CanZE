from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620731():
    client = ReplayUDSClient(sid_responses={"220731": ['046207315A000000']})
    assert client.read_field("76d.24.620731") == pytest.approx(90.0)
