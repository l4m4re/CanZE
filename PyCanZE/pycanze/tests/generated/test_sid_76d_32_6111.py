from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_32_6111():
    client = ReplayUDSClient(sid_responses={"2111": ['10086111CF8F8F8F', '2100000000000000']})
    assert client.read_field("76d.32.6111") == pytest.approx(143.0)
