from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_620700():
    client = ReplayUDSClient(sid_responses={"220700": ['0462070014000000']})
    assert client.read_field("76d.24.620700") == pytest.approx(0.3)
