from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62223c():
    client = ReplayUDSClient(sid_responses={"22223C": ['0562223CFFE0AAAA']})
    assert client.read_field("7ec.24.62223c") == pytest.approx(1647.0)
