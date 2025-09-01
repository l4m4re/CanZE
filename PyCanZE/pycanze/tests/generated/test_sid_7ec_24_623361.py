from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623361():
    client = ReplayUDSClient(sid_responses={"223361": ['07623361013FBAD2']})
    assert client.read_field("7ec.24.623361") == pytest.approx(20953810.0)
