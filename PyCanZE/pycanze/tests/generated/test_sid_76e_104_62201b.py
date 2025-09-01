from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_104_62201b():
    client = ReplayUDSClient(sid_responses={"22201B": ['101062201B000000', '2100000000000000', '2200000000000000']})
    assert client.read_field("76e.104.62201b") == pytest.approx(0.0)
