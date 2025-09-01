from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_88_62f804():
    client = ReplayUDSClient(sid_responses={"22F804": ['102362F804484D4C', '2147543434333352', '2200000000000030', '2330303030303030', '2430303030303030', '2530AAAAAAAAAAAA']})
    assert client.read_field("7ec.88.62f804") == pytest.approx(861011968.0)
