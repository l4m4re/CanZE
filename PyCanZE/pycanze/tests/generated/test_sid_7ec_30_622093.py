from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_622093():
    client = ReplayUDSClient(sid_responses={"222093": ['0462209302AAAAAA']})
    assert client.read_field("7ec.30.622093") == pytest.approx(2.0)
