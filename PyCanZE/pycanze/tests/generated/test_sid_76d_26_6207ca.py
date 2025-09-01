from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_26_6207ca():
    client = ReplayUDSClient(sid_responses={"2207CA": ['056207CA23280000']})
    assert client.read_field("76d.26.6207ca") == pytest.approx(90.0)
