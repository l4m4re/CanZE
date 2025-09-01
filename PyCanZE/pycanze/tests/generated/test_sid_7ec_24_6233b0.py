from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6233b0():
    client = ReplayUDSClient(sid_responses={"2233B0": ['056233B00B0EAAAA']})
    assert client.read_field("7ec.24.6233b0") == pytest.approx(10.0)
