from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6234b2():
    client = ReplayUDSClient(sid_responses={"2234B2": ['046234B200AAAAAA']})
    assert client.read_field("7ec.30.6234b2") == pytest.approx(0.0)
