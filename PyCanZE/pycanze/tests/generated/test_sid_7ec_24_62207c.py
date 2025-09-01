from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62207c():
    client = ReplayUDSClient(sid_responses={"22207C": ['0462207C03AAAAAA']})
    assert client.read_field("7ec.24.62207c") == pytest.approx(3.0)
