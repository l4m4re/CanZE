from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_72_623545():
    client = ReplayUDSClient(sid_responses={"223545": ['101362354580D680', '2118801880168016', '228015801480D6AA']})
    assert client.read_field("7ec.72.623545") == pytest.approx(88.0)
