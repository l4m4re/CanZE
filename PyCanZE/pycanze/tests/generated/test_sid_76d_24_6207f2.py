from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207f2():
    client = ReplayUDSClient(sid_responses={"2207F2": ['046207F203000000']})
    assert client.read_field("76d.24.6207f2") == pytest.approx(0.0)
