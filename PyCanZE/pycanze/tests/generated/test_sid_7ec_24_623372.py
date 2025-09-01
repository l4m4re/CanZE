from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623372():
    client = ReplayUDSClient(sid_responses={"223372": ['04623372FEAAAAAA']})
    assert client.read_field("7ec.24.623372") == pytest.approx(1270.0)
