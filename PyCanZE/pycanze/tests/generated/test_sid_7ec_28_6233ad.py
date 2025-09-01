from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_28_6233ad():
    client = ReplayUDSClient(sid_responses={"2233AD": ['046233AD00AAAAAA']})
    assert client.read_field("7ec.28.6233ad") == pytest.approx(0.0)
