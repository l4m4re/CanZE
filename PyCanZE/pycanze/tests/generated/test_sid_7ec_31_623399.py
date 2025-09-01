from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_31_623399():
    client = ReplayUDSClient(sid_responses={"223399": ['0462339900AAAAAA']})
    assert client.read_field("7ec.31.623399") == pytest.approx(0.0)
