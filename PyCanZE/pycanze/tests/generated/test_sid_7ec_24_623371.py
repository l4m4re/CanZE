from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623371():
    client = ReplayUDSClient(sid_responses={"223371": ['04623371FEAAAAAA']})
    assert client.read_field("7ec.24.623371") == pytest.approx(1270.0)
