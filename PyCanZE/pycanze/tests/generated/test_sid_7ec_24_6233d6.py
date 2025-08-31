from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6233d6():
    client = ReplayUDSClient(sid_responses={"2233D6": ['100D6233D6000000', '2100000000000000']})
    assert client.read_field("7ec.24.6233d6") == pytest.approx(0.0)
