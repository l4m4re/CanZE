from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6234be():
    client = ReplayUDSClient(sid_responses={"2234BE": ['056234BE05A0AAAA']})
    assert client.read_field("7ec.24.6234be") == pytest.approx(1440.0)
