from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_28_6233e6():
    client = ReplayUDSClient(sid_responses={"2233E6": ['046233E600AAAAAA']})
    assert client.read_field("7ec.28.6233e6") == pytest.approx(0.0)
