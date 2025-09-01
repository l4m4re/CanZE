from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bb_96_6166():
    client = ReplayUDSClient(sid_responses={"2166": ['100E6166000103AC', '210142026A000200', '2201000000000000']})
    assert client.read_field("7bb.96.6166") == pytest.approx(1.0)
