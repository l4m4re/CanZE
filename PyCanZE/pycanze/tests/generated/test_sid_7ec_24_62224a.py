from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62224a():
    client = ReplayUDSClient(sid_responses={"22224A": ['0562224A5330AAAA']})
    assert client.read_field("7ec.24.62224a") == pytest.approx(13.323)
