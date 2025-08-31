from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_622005():
    client = ReplayUDSClient(sid_responses={"222005": ['0562200504CDAAAA']})
    assert client.read_field("7ec.24.622005") == pytest.approx(12.29)
