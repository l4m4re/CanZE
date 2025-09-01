from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623484():
    client = ReplayUDSClient(sid_responses={"223484": ['056234848096AAAA']})
    assert client.read_field("7ec.24.623484") == pytest.approx(150.0)
