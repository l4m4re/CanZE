from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62352e():
    client = ReplayUDSClient(sid_responses={"22352E": ['0462352E14AAAAAA']})
    assert client.read_field("7ec.24.62352e") == pytest.approx(10.0)
