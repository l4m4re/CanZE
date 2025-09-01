from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6233eb():
    client = ReplayUDSClient(sid_responses={"2233EB": ['046233EB00AAAAAA']})
    assert client.read_field("7ec.30.6233eb") == pytest.approx(0.0)
