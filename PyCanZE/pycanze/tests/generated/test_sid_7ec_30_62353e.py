from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_62353e():
    client = ReplayUDSClient(sid_responses={"22353E": ['0462353E00AAAAAA']})
    assert client.read_field("7ec.30.62353e") == pytest.approx(0.0)
