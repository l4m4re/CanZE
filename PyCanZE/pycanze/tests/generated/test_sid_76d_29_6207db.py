from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_29_6207db():
    client = ReplayUDSClient(sid_responses={"2207DB": ['066207DB00000000']})
    assert client.read_field("76d.29.6207db") == pytest.approx(0.0)
