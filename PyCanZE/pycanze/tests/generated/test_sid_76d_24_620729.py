from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620729():
    client = ReplayUDSClient(sid_responses={"220729": ['0462072932000000']})
    assert client.read_field("76d.24.620729") == pytest.approx(11.2)
