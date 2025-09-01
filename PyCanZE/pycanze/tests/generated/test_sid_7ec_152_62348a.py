from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_152_62348a():
    client = ReplayUDSClient(sid_responses={"22348A": ['102B62348A7F767F', '21B17FB17FB17FB2', '227F9F7FB17FB17F', '23B17FB17FB17FB1', '247FB17FB17FB17F', '25B17FB07FB17FB0', '267FB2AAAAAAAAAA']})
    assert client.read_field("7ec.152.62348a") == pytest.approx(-79.0)
