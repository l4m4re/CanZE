from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_30_6234de():
    client = ReplayUDSClient(sid_responses={"2234DE": ['046234DE01AAAAAA']})
    assert client.read_field("7ec.30.6234de") == pytest.approx(1.0)
