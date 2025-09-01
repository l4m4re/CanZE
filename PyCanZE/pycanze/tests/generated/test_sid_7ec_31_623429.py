from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623429():
    client = ReplayUDSClient(sid_responses={"223429": ['0462342900AAAAAA']})
    assert client.read_field("7ec.31.623429") == pytest.approx(0.0)
