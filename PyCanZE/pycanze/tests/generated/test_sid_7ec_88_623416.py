from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_88_623416():
    client = ReplayUDSClient(sid_responses={"223416": ['1017623416002E00', '212E002E00340070', '2200C600FF00FF00', '23FF00FFAAAAAAAA']})
    assert client.read_field("7ec.88.623416") == pytest.approx(1.12)
