from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620726():
    client = ReplayUDSClient(sid_responses={"220726": ['0462072606000000']})
    assert client.read_field("76d.24.620726") == pytest.approx(240.0)
