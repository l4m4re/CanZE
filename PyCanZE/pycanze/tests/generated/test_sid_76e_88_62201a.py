from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_88_62201a():
    client = ReplayUDSClient(sid_responses={"22201A": ['101062201A0B0B0D', '2110121212141210', '220D0D0812141210']})
    assert client.read_field("76e.88.62201a") == pytest.approx(18.0)
