from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6233dd():
    client = ReplayUDSClient(sid_responses={"2233DD": ['066233DD01ED9CAA']})
    assert client.read_field("7ec.24.6233dd") == pytest.approx(126.364)
