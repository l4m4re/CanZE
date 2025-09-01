from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_623410():
    client = ReplayUDSClient(sid_responses={"223410": ['0462341001AAAAAA']})
    assert client.read_field("7ec.29.623410") == pytest.approx(1.0)
