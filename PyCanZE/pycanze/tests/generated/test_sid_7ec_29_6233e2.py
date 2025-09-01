from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_6233e2():
    client = ReplayUDSClient(sid_responses={"2233E2": ['046233E204AAAAAA']})
    assert client.read_field("7ec.29.6233e2") == pytest.approx(4.0)
