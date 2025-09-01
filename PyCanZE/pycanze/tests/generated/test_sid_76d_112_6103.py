from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_112_6103():
    client = ReplayUDSClient(sid_responses={"2103": ['1021610330000000', '2100000000000000', '2200FE0000000000', '2300000000000000', '2400000001000000']})
    assert client.read_field("76d.112.6103") == pytest.approx(254.0)
