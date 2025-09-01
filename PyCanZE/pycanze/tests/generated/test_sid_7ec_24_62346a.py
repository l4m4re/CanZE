from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62346a():
    client = ReplayUDSClient(sid_responses={"22346A": ['0462346A78AAAAAA']})
    assert client.read_field("7ec.24.62346a") == pytest.approx(80.0)
