from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_168_623415():
    client = ReplayUDSClient(sid_responses={"223415": ['1017623415075607', '219907CE0FF50E99', '220E370A650A880A', '23DF0BCEAAAAAAAA']})
    assert client.read_field("7ec.168.623415") == pytest.approx(60.44)
