from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_62352a():
    client = ReplayUDSClient(sid_responses={"22352A": ['0462352A00AAAAAA']})
    assert client.read_field("7ec.30.62352a") == pytest.approx(0.0)
