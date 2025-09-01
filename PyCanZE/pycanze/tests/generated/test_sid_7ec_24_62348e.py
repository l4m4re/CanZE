from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62348e():
    client = ReplayUDSClient(sid_responses={"22348E": ['0462348E1EAAAAAA']})
    assert client.read_field("7ec.24.62348e") == pytest.approx(13.5)
