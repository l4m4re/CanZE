from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62320c():
    client = ReplayUDSClient(sid_responses={"22320C": ['0562320C0CA5AAAA']})
    assert client.read_field("7ec.24.62320c") == pytest.approx(16.185)
