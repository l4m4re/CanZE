from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623438():
    client = ReplayUDSClient(sid_responses={"223438": ['04623438A0AAAAAA']})
    assert client.read_field("7ec.24.623438") == pytest.approx(120.0)
