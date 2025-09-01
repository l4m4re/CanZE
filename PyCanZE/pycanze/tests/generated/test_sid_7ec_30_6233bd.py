from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6233bd():
    client = ReplayUDSClient(sid_responses={"2233BD": ['046233BD02AAAAAA']})
    assert client.read_field("7ec.30.6233bd") == pytest.approx(2.0)
