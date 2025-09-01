from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6234b9():
    client = ReplayUDSClient(sid_responses={"2234B9": ['046234B900AAAAAA']})
    assert client.read_field("7ec.30.6234b9") == pytest.approx(0.0)
