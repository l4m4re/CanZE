from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623325():
    client = ReplayUDSClient(sid_responses={"223325": ['0462332500AAAAAA']})
    assert client.read_field("7ec.31.623325") == pytest.approx(0.0)
