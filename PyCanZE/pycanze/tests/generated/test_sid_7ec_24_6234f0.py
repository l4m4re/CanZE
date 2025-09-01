from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234f0():
    client = ReplayUDSClient(sid_responses={"2234F0": ['046234F000AAAAAA']})
    assert client.read_field("7ec.24.6234f0") == pytest.approx(0.0)
