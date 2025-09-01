from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623502():
    client = ReplayUDSClient(sid_responses={"223502": ['0462350201AAAAAA']})
    assert client.read_field("7ec.24.623502") == pytest.approx(1.0)
