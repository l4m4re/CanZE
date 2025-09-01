from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620728():
    client = ReplayUDSClient(sid_responses={"220728": ['0462072814000000']})
    assert client.read_field("76d.24.620728") == pytest.approx(10.5)
