from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6234b0():
    client = ReplayUDSClient(sid_responses={"2234B0": ['046234B000AAAAAA']})
    assert client.read_field("7ec.31.6234b0") == pytest.approx(0.0)
