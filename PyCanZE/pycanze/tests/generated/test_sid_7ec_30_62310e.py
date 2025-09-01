from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_62310e():
    client = ReplayUDSClient(sid_responses={"22310E": ['0462310E00AAAAAA']})
    assert client.read_field("7ec.30.62310e") == pytest.approx(0.0)
