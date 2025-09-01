from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_24_6102():
    client = ReplayUDSClient(sid_responses={"2102": ['1020610204EE0018', '2100000000000300', '2226000000000003', '23002A04E7000000', '240001C804E30000']})
    assert client.read_field("76d.24.6102") == pytest.approx(238.0)
