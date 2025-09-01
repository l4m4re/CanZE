from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bb_190_6103():
    client = ReplayUDSClient(sid_responses={"2103": ['101D6103016D1243', '21132E0000000001', '226E016D000000FF', '23FF07D00512D600', '2400010000000000']})
    assert client.read_field("7bb.190.6103") == pytest.approx(1.0)
