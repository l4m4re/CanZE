from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_6234b7():
    client = ReplayUDSClient(sid_responses={"2234B7": ['046234B701AAAAAA']})
    assert client.read_field("7ec.29.6234b7") == pytest.approx(1.0)
