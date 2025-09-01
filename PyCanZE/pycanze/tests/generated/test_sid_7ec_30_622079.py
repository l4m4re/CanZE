from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_622079():
    client = ReplayUDSClient(sid_responses={"222079": ['0462207900AAAAAA']})
    assert client.read_field("7ec.30.622079") == pytest.approx(0.0)
