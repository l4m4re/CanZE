from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_48_62201c():
    client = ReplayUDSClient(sid_responses={"22201C": ['101062201C000000', '2100000000000000', '2200000000000000']})
    assert client.read_field("76e.48.62201c") == pytest.approx(0.0)
