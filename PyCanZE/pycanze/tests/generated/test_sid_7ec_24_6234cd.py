from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234cd():
    client = ReplayUDSClient(sid_responses={"2234CD": ['056234CD01C2AAAA']})
    assert client.read_field("7ec.24.6234cd") == pytest.approx(450.0)
