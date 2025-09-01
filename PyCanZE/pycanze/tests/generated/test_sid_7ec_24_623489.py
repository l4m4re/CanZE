from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623489():
    client = ReplayUDSClient(sid_responses={"223489": ['076234890070B660']})
    assert client.read_field("7ec.24.623489") == pytest.approx(7386720.0)
