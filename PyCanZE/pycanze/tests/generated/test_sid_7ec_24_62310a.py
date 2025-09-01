from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62310a():
    client = ReplayUDSClient(sid_responses={"22310A": ['0462310A64AAAAAA']})
    assert client.read_field("7ec.24.62310a") == pytest.approx(100.0)
