from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_88_6105():
    client = ReplayUDSClient(sid_responses={"2105": ['1011610500000000', '2100000000000000', '2200000000000000']})
    assert client.read_field("76d.88.6105") == pytest.approx(0.0)
