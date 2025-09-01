from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620709():
    client = ReplayUDSClient(sid_responses={"220709": ['0462070900000000']})
    assert client.read_field("76d.24.620709") == pytest.approx(0.16)
