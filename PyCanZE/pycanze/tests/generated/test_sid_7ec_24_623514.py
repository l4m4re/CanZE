from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623514():
    client = ReplayUDSClient(sid_responses={"223514": ['0462351400AAAAAA']})
    assert client.read_field("7ec.24.623514") == pytest.approx(0.0)
