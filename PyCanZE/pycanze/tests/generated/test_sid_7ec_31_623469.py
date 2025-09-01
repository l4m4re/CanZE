from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623469():
    client = ReplayUDSClient(sid_responses={"223469": ['0462346900AAAAAA']})
    assert client.read_field("7ec.31.623469") == pytest.approx(0.0)
