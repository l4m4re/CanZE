from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6233bc():
    client = ReplayUDSClient(sid_responses={"2233BC": ['046233BC01AAAAAA']})
    assert client.read_field("7ec.30.6233bc") == pytest.approx(1.0)
