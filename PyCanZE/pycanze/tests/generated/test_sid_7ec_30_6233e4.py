from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6233e4():
    client = ReplayUDSClient(sid_responses={"2233E4": ['046233E402AAAAAA']})
    assert client.read_field("7ec.30.6233e4") == pytest.approx(2.0)
