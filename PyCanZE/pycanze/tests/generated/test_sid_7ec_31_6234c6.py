from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6234c6():
    client = ReplayUDSClient(sid_responses={"2234C6": ['046234C600AAAAAA']})
    assert client.read_field("7ec.31.6234c6") == pytest.approx(0.0)
