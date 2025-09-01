from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623208():
    client = ReplayUDSClient(sid_responses={"223208": ['0462320800AAAAAA']})
    assert client.read_field("7ec.30.623208") == pytest.approx(0.0)
