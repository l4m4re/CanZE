from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_6233de():
    client = ReplayUDSClient(sid_responses={"2233DE": ['076233DE00870CA8']})
    assert client.read_field("7ec.24.6233de") == pytest.approx(885.06)
