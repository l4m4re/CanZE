from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234c8():
    client = ReplayUDSClient(sid_responses={"2234C8": ['046234C832AAAAAA']})
    assert client.read_field("7ec.24.6234c8") == pytest.approx(5.0)
