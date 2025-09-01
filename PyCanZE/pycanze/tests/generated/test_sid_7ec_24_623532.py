from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623532():
    client = ReplayUDSClient(sid_responses={"223532": ['0462353200AAAAAA']})
    assert client.read_field("7ec.24.623532") == pytest.approx(0.0)
