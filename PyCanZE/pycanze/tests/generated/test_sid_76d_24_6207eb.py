from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6207eb():
    client = ReplayUDSClient(sid_responses={"2207EB": ['046207EB00000000']})
    assert client.read_field("76d.24.6207eb") == pytest.approx(0.0)
