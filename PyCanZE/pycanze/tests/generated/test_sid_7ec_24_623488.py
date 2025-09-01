from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623488():
    client = ReplayUDSClient(sid_responses={"223488": ['07623488001D4FD7']})
    assert client.read_field("7ec.24.623488") == pytest.approx(1920983.0)
