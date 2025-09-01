from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623396():
    client = ReplayUDSClient(sid_responses={"223396": ['0462339600AAAAAA']})
    assert client.read_field("7ec.31.623396") == pytest.approx(0.0)
