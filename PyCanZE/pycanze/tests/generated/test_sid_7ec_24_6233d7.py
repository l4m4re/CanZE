from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6233d7():
    client = ReplayUDSClient(sid_responses={"2233D7": ['10176233D700BB00', '21C200C701980175', '22016B010A010D01', '2316012EAAAAAAAA']})
    assert client.read_field("7ec.24.6233d7") == pytest.approx(37.4)
