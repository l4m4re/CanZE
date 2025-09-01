from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623441():
    client = ReplayUDSClient(sid_responses={"223441": ['0462344100AAAAAA']})
    assert client.read_field("7ec.31.623441") == pytest.approx(0.0)
