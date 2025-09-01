from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623337():
    client = ReplayUDSClient(sid_responses={"223337": ['0462333701AAAAAA']})
    assert client.read_field("7ec.30.623337") == pytest.approx(1.0)
