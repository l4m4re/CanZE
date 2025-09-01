from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620727():
    client = ReplayUDSClient(sid_responses={"220727": ['0462072705000000']})
    assert client.read_field("76d.24.620727") == pytest.approx(200.0)
