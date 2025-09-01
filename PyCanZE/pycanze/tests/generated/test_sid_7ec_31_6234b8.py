from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6234b8():
    client = ReplayUDSClient(sid_responses={"2234B8": ['046234B800AAAAAA']})
    assert client.read_field("7ec.31.6234b8") == pytest.approx(0.0)
