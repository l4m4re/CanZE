from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234ca():
    client = ReplayUDSClient(sid_responses={"2234CA": ['046234CA14AAAAAA']})
    assert client.read_field("7ec.24.6234ca") == pytest.approx(500.0)
