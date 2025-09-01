from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623111():
    client = ReplayUDSClient(sid_responses={"223111": ['0462311100AAAAAA']})
    assert client.read_field("7ec.31.623111") == pytest.approx(0.0)
