from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623377():
    client = ReplayUDSClient(sid_responses={"223377": ['0462337700AAAAAA']})
    assert client.read_field("7ec.30.623377") == pytest.approx(0.0)
