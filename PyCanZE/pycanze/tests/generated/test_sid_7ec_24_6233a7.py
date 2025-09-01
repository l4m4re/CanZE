from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6233a7():
    client = ReplayUDSClient(sid_responses={"2233A7": ['046233A7FEAAAAAA']})
    assert client.read_field("7ec.24.6233a7") == pytest.approx(6350.0)
