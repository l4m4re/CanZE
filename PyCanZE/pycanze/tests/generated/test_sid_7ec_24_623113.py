from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623113():
    client = ReplayUDSClient(sid_responses={"223113": ['0462311300AAAAAA']})
    assert client.read_field("7ec.24.623113") == pytest.approx(0.0)
