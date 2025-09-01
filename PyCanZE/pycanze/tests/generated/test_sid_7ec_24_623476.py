from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623476():
    client = ReplayUDSClient(sid_responses={"223476": ['1009623476000000', '21000000AAAAAAAA']})
    assert client.read_field("7ec.24.623476") == pytest.approx(0.0)
