from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_184_61f0():
    client = ReplayUDSClient(sid_responses={"21F0": ['101A61F031373133', '2152354145303330', '22393152650A0000', '2300000201008800']})
    assert client.read_field("7ec.184.61f0") == pytest.approx(1.0)
