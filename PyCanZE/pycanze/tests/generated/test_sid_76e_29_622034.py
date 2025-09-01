from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_29_622034():
    client = ReplayUDSClient(sid_responses={"222034": ['0462203408000000']})
    assert client.read_field("76e.29.622034") == pytest.approx(0.0)
