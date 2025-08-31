from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_56_6233d8():
    client = ReplayUDSClient(sid_responses={"2233D8": ['100D6233D8414242', '21413F3F3B3B3B3B']})
    assert client.read_field("7ec.56.6233d8") == pytest.approx(23.0)
