from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234d1():
    client = ReplayUDSClient(sid_responses={"2234D1": ['066234D170B1CBAA']})
    assert client.read_field("7ec.24.6234d1") == pytest.approx(7385.547)
