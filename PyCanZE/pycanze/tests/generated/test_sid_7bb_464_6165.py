from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bb_464_6165():
    client = ReplayUDSClient(sid_responses={"2165": ['103E6165000000FF', '2194490B90000000', '22FF960400FFA9DB', '230B6C88FB00FF00', '240000FF8BED00FF', '25AB8200DD000000', '26FF000000FFCA32', '2700FC000000FF00', '280000FFC7B600FF']})
    assert client.read_field("7bb.464.6165") == pytest.approx(99.855)
