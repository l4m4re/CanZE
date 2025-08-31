from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_168_6233d9():
    client = ReplayUDSClient(sid_responses={"2233D9": ['10176233D9000000', '2119000601B001D8', '22026B0000000C00', '231C005FAAAAAAAA']})
    assert client.read_field("7ec.168.6233d9") == pytest.approx(95.0)
