from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234cc():
    client = ReplayUDSClient(sid_responses={"2234CC": ['056234CC0195AAAA']})
    assert client.read_field("7ec.24.6234cc") == pytest.approx(405.0)
