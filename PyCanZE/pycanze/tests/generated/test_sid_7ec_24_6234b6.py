from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234b6():
    client = ReplayUDSClient(sid_responses={"2234B6": ['046234B600AAAAAA']})
    assert client.read_field("7ec.24.6234b6") == pytest.approx(0.0)
