from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_622226():
    client = ReplayUDSClient(sid_responses={"222226": ['0462222600AAAAAA']})
    assert client.read_field("7ec.31.622226") == pytest.approx(0.0)
