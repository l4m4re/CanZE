from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_88_623546():
    client = ReplayUDSClient(sid_responses={"223546": ['1013623546E418E4', '2118E418E418E418', '22E418E418E418AA']})
    assert client.read_field("7ec.88.623546") == pytest.approx(29.196)
