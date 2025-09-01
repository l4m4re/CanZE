from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62349e():
    client = ReplayUDSClient(sid_responses={"22349E": ['0462349E00AAAAAA']})
    assert client.read_field("7ec.31.62349e") == pytest.approx(0.0)
