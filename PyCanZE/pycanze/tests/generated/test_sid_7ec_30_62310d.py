from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_62310d():
    client = ReplayUDSClient(sid_responses={"22310D": ['0462310D00AAAAAA']})
    assert client.read_field("7ec.30.62310d") == pytest.approx(0.0)
