from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_29_623536():
    client = ReplayUDSClient(sid_responses={"223536": ['0462353603AAAAAA']})
    assert client.read_field("7ec.29.623536") == pytest.approx(3.0)
