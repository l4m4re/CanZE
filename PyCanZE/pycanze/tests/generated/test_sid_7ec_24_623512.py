from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623512():
    client = ReplayUDSClient(sid_responses={"223512": ['0462351202AAAAAA']})
    assert client.read_field("7ec.24.623512") == pytest.approx(2.0)
