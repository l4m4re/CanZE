from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_62070a():
    client = ReplayUDSClient(sid_responses={"22070A": ['0462070A3C000000']})
    assert client.read_field("76d.24.62070a") == pytest.approx(600.0)
