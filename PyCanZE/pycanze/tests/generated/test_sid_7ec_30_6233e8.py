from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6233e8():
    client = ReplayUDSClient(sid_responses={"2233E8": ['046233E800AAAAAA']})
    assert client.read_field("7ec.30.6233e8") == pytest.approx(0.0)
