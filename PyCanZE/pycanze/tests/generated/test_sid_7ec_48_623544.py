from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_48_623544():
    client = ReplayUDSClient(sid_responses={"223544": ['1023623544000000', '213BC37F3BC3423B', '22C2D83BC2C63BC2', '23973BC26B000000', '2400000000000000', '2500AAAAAAAAAAAA']})
    assert client.read_field("7ec.48.623544") == pytest.approx(3916671.0)
