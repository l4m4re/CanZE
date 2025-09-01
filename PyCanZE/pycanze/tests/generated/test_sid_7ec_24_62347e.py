from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62347e():
    client = ReplayUDSClient(sid_responses={"22347E": ['0562347E05B4AAAA']})
    assert client.read_field("7ec.24.62347e") == pytest.approx(1460.0)
