from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6233fc():
    client = ReplayUDSClient(sid_responses={"2233FC": ['046233FC01AAAAAA']})
    assert client.read_field("7ec.30.6233fc") == pytest.approx(1.0)
