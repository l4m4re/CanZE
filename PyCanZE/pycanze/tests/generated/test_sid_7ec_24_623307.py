from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623307():
    client = ReplayUDSClient(sid_responses={"223307": ['046233073CAAAAAA']})
    assert client.read_field("7ec.24.623307") == pytest.approx(20.0)
