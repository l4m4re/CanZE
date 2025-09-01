from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620724():
    client = ReplayUDSClient(sid_responses={"220724": ['0462072401000000']})
    assert client.read_field("76d.24.620724") == pytest.approx(40.0)
