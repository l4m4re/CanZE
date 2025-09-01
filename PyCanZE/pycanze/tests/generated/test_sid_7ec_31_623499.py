from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623499():
    client = ReplayUDSClient(sid_responses={"223499": ['0462349900AAAAAA']})
    assert client.read_field("7ec.31.623499") == pytest.approx(0.0)
