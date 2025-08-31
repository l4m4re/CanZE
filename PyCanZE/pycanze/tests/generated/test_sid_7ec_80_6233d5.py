from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_80_6233d5():
    client = ReplayUDSClient(sid_responses={"2233D5": ['100D6233D5020201', '2101010102020201']})
    assert client.read_field("7ec.80.6233d5") == pytest.approx(2.0)
