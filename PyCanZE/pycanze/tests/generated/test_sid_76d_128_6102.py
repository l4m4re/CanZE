from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_128_6102():
    client = ReplayUDSClient(sid_responses={"2102": ['1020610204EE0018', '2100000000000300', '2226000000000003', '23002A04E7000000', '240001C804E30000']})
    assert client.read_field("76d.128.6102") == pytest.approx(0.0)
