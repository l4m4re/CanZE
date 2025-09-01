from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620749():
    client = ReplayUDSClient(sid_responses={"220749": ['0462074904000000']})
    assert client.read_field("76d.24.620749") == pytest.approx(0.0)
