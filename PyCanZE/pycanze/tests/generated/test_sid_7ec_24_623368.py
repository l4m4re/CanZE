from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623368():
    client = ReplayUDSClient(sid_responses={"223368": ['07623368005D65AB']})
    assert client.read_field("7ec.24.623368") == pytest.approx(6120875.0)
