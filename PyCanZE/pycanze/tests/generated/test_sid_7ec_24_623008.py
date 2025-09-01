from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623008():
    client = ReplayUDSClient(sid_responses={"223008": ['0562300803FEAAAA']})
    assert client.read_field("7ec.24.623008") == pytest.approx(511.0)
