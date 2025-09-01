from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62352b():
    client = ReplayUDSClient(sid_responses={"22352B": ['0462352B00AAAAAA']})
    assert client.read_field("7ec.31.62352b") == pytest.approx(0.0)
