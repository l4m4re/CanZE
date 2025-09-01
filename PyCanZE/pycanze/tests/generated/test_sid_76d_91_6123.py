from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_91_6123():
    client = ReplayUDSClient(sid_responses={"2123": ['100C61230007D03C', '2100000000000000']})
    assert client.read_field("76d.91.6123") == pytest.approx(0.0)
