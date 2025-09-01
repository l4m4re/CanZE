from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623497():
    client = ReplayUDSClient(sid_responses={"223497": ['0462349700AAAAAA']})
    assert client.read_field("7ec.31.623497") == pytest.approx(0.0)
