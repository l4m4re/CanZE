from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623001():
    client = ReplayUDSClient(sid_responses={"223001": ['0462300100AAAAAA']})
    assert client.read_field("7ec.30.623001") == pytest.approx(0.0)
