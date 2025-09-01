from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623537():
    client = ReplayUDSClient(sid_responses={"223537": ['046235371EAAAAAA']})
    assert client.read_field("7ec.24.623537") == pytest.approx(150.0)
