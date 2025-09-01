from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623528():
    client = ReplayUDSClient(sid_responses={"223528": ['0462352800AAAAAA']})
    assert client.read_field("7ec.31.623528") == pytest.approx(0.0)
