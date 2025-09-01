from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234f8():
    client = ReplayUDSClient(sid_responses={"2234F8": ['046234F878AAAAAA']})
    assert client.read_field("7ec.24.6234f8") == pytest.approx(80.0)
