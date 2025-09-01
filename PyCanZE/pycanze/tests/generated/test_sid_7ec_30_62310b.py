from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_62310b():
    client = ReplayUDSClient(sid_responses={"22310B": ['0462310B00AAAAAA']})
    assert client.read_field("7ec.30.62310b") == pytest.approx(0.0)
