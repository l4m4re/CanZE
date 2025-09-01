from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623432():
    client = ReplayUDSClient(sid_responses={"223432": ['056234326418AAAA']})
    assert client.read_field("7ec.24.623432") == pytest.approx(12.812)
