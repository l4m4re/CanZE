from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623521():
    client = ReplayUDSClient(sid_responses={"223521": ['0462352100AAAAAA']})
    assert client.read_field("7ec.30.623521") == pytest.approx(0.0)
