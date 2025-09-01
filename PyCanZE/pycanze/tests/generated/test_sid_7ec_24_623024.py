from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623024():
    client = ReplayUDSClient(sid_responses={"223024": ['04623024A0AAAAAA']})
    assert client.read_field("7ec.24.623024") == pytest.approx(20.0)
