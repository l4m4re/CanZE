from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234fc():
    client = ReplayUDSClient(sid_responses={"2234FC": ['046234FC3CAAAAAA']})
    assert client.read_field("7ec.24.6234fc") == pytest.approx(20.0)
