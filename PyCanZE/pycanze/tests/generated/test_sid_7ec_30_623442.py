from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623442():
    client = ReplayUDSClient(sid_responses={"223442": ['0462344202AAAAAA']})
    assert client.read_field("7ec.30.623442") == pytest.approx(2.0)
