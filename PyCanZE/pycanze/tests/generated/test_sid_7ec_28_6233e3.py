from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_28_6233e3():
    client = ReplayUDSClient(sid_responses={"2233E3": ['046233E300AAAAAA']})
    assert client.read_field("7ec.28.6233e3") == pytest.approx(0.0)
