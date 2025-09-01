from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234ad():
    client = ReplayUDSClient(sid_responses={"2234AD": ['056234AD8024AAAA']})
    assert client.read_field("7ec.24.6234ad") == pytest.approx(3.6)
