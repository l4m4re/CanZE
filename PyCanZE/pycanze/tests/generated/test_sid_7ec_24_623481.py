from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623481():
    client = ReplayUDSClient(sid_responses={"223481": ['0462348100AAAAAA']})
    assert client.read_field("7ec.24.623481") == pytest.approx(0.0)
