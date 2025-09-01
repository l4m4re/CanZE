from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_623374():
    client = ReplayUDSClient(sid_responses={"223374": ['0462337400AAAAAA']})
    assert client.read_field("7ec.30.623374") == pytest.approx(0.0)
