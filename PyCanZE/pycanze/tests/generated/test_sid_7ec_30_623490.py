from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623490():
    client = ReplayUDSClient(sid_responses={"223490": ['0462349000AAAAAA']})
    assert client.read_field("7ec.30.623490") == pytest.approx(0.0)
