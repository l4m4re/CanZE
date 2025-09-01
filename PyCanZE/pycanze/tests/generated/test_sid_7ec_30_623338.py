from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623338():
    client = ReplayUDSClient(sid_responses={"223338": ['0462333801AAAAAA']})
    assert client.read_field("7ec.30.623338") == pytest.approx(1.0)
