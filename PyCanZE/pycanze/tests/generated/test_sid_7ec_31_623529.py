from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623529():
    client = ReplayUDSClient(sid_responses={"223529": ['0462352900AAAAAA']})
    assert client.read_field("7ec.31.623529") == pytest.approx(0.0)
