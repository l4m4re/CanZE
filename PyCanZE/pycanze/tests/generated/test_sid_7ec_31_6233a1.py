from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6233a1():
    client = ReplayUDSClient(sid_responses={"2233A1": ['046233A100AAAAAA']})
    assert client.read_field("7ec.31.6233a1") == pytest.approx(0.0)
