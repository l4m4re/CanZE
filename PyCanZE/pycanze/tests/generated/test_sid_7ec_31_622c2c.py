from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_622c2c():
    client = ReplayUDSClient(sid_responses={"222C2C": ['04622C2C00AAAAAA']})
    assert client.read_field("7ec.31.622c2c") == pytest.approx(0.0)
