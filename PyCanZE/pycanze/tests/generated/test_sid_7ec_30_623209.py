from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623209():
    client = ReplayUDSClient(sid_responses={"223209": ['0462320901AAAAAA']})
    assert client.read_field("7ec.30.623209") == pytest.approx(1.0)
