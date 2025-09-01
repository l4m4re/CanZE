from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62336a():
    client = ReplayUDSClient(sid_responses={"22336A": ['0462336A55AAAAAA']})
    assert client.read_field("7ec.24.62336a") == pytest.approx(85.0)
