from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_25_623109():
    client = ReplayUDSClient(sid_responses={"223109": ['046231091EAAAAAA']})
    assert client.read_field("7ec.25.623109") == pytest.approx(30.0)
