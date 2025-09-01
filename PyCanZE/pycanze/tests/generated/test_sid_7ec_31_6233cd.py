from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_6233cd():
    client = ReplayUDSClient(sid_responses={"2233CD": ['046233CD00AAAAAA']})
    assert client.read_field("7ec.31.6233cd") == pytest.approx(0.0)
