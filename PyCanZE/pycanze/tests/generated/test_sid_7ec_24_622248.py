from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_622248():
    client = ReplayUDSClient(sid_responses={"222248": ['0562224885A0AAAA']})
    assert client.read_field("7ec.24.622248") == pytest.approx(720.0)
