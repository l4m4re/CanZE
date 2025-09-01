from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62200c():
    client = ReplayUDSClient(sid_responses={"22200C": ['0562200C0173AAAA']})
    assert client.read_field("7ec.24.62200c") == pytest.approx(371.0)
