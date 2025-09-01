from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7bc_32_6184():
    client = ReplayUDSClient(sid_responses={"2184": ['1016618430304642', '2130324534353933', '2231303331382020', '2320200000000000']})
    assert client.read_field("7bc.32.6184") == pytest.approx(2.0)
