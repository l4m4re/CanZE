from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623454():
    client = ReplayUDSClient(sid_responses={"223454": ['1009623454004FF3', '21000803AAAAAAAA']})
    assert client.read_field("7ec.24.623454") == pytest.approx(20.467)
