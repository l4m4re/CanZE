from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_62206e():
    client = ReplayUDSClient(sid_responses={"22206E": ['0462206E00AAAAAA']})
    assert client.read_field("7ec.31.62206e") == pytest.approx(0.0)
