from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_80_622019():
    client = ReplayUDSClient(sid_responses={"222019": ['10106220190B0B0D', '2110121212141210', '220D0D0812141210']})
    assert client.read_field("76e.80.622019") == pytest.approx(20.0)
