from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_622221():
    client = ReplayUDSClient(sid_responses={"222221": ['0462222100AAAAAA']})
    assert client.read_field("7ec.31.622221") == pytest.approx(0.0)
