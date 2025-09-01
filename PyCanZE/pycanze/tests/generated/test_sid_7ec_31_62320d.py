from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62320d():
    client = ReplayUDSClient(sid_responses={"22320D": ['0562320D0000AAAA']})
    assert client.read_field("7ec.31.62320d") == pytest.approx(0.0)
