from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6234d0():
    client = ReplayUDSClient(sid_responses={"2234D0": ['046234D000AAAAAA']})
    assert client.read_field("7ec.31.6234d0") == pytest.approx(0.0)
