from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_28_623523():
    client = ReplayUDSClient(sid_responses={"223523": ['0462352300AAAAAA']})
    assert client.read_field("7ec.28.623523") == pytest.approx(0.0)
