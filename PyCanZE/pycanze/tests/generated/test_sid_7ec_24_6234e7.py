from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234e7():
    client = ReplayUDSClient(sid_responses={"2234E7": ['056234E701CCAAAA']})
    assert client.read_field("7ec.24.6234e7") == pytest.approx(200.0)
