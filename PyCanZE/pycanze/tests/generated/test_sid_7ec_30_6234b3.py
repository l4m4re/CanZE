from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6234b3():
    client = ReplayUDSClient(sid_responses={"2234B3": ['046234B300AAAAAA']})
    assert client.read_field("7ec.30.6234b3") == pytest.approx(0.0)
