from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6233b1():
    client = ReplayUDSClient(sid_responses={"2233B1": ['046233B1FEAAAAAA']})
    assert client.read_field("7ec.24.6233b1") == pytest.approx(214.0)
