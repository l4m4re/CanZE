from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623336():
    client = ReplayUDSClient(sid_responses={"223336": ['0462333601AAAAAA']})
    assert client.read_field("7ec.30.623336") == pytest.approx(1.0)
