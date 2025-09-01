from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623498():
    client = ReplayUDSClient(sid_responses={"223498": ['0462349800AAAAAA']})
    assert client.read_field("7ec.31.623498") == pytest.approx(0.0)
