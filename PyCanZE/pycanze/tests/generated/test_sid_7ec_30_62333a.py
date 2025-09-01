from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_62333a():
    client = ReplayUDSClient(sid_responses={"22333A": ['0462333A00AAAAAA']})
    assert client.read_field("7ec.30.62333a") == pytest.approx(0.0)
