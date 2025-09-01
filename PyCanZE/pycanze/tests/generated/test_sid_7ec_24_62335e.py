from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62335e():
    client = ReplayUDSClient(sid_responses={"22335E": ['0762335E005942D3']})
    assert client.read_field("7ec.24.62335e") == pytest.approx(5849811.0)
