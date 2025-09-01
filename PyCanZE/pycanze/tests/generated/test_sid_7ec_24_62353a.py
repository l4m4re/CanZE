from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62353a():
    client = ReplayUDSClient(sid_responses={"22353A": ['0562353A01CCAAAA']})
    assert client.read_field("7ec.24.62353a") == pytest.approx(200.0)
