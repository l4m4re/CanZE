from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_72_62203b():
    client = ReplayUDSClient(sid_responses={"22203B": ['100D62203BFFF303', '2181361807800209']})
    assert client.read_field("76e.72.62203b") == pytest.approx(7.0)
