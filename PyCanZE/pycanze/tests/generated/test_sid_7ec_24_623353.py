from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623353():
    client = ReplayUDSClient(sid_responses={"223353": ['0762335301EB15CB']})
    assert client.read_field("7ec.24.623353") == pytest.approx(32183755.0)
