from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_24_62203a():
    client = ReplayUDSClient(sid_responses={"22203A": ['0762203A00000000']})
    assert client.read_field("76e.24.62203a") == pytest.approx(0.0)
