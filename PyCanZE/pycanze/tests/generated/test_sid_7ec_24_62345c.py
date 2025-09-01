from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62345c():
    client = ReplayUDSClient(sid_responses={"22345C": ['0462345C00AAAAAA']})
    assert client.read_field("7ec.24.62345c") == pytest.approx(0.0)
