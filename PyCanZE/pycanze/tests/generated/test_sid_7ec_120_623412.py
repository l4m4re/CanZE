from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_120_623412():
    client = ReplayUDSClient(sid_responses={"223412": ['1017623412063D06', '213D063D068B102F', '2216E31A021A021A', '23021A02AAAAAAAA']})
    assert client.read_field("7ec.120.623412") == pytest.approx(66.58)
