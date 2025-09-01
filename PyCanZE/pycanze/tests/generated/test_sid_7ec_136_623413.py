from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_136_623413():
    client = ReplayUDSClient(sid_responses={"223413": ['1017623413057F05', '217F057F05C60E6D', '2214291679167916', '23791679AAAAAAAA']})
    assert client.read_field("7ec.136.623413") == pytest.approx(57.53)
