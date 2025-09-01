from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620725():
    client = ReplayUDSClient(sid_responses={"220725": ['0462072503000000']})
    assert client.read_field("76d.24.620725") == pytest.approx(120.0)
