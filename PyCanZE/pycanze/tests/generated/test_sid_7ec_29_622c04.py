from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_622c04():
    client = ReplayUDSClient(sid_responses={"222C04": ['04622C0401AAAAAA']})
    assert client.read_field("7ec.29.622c04") == pytest.approx(0.0)
