from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_622022():
    client = ReplayUDSClient(sid_responses={"222022": ['056220221388AAAA']})
    assert client.read_field("7ec.24.622022") == pytest.approx(5000.0)
