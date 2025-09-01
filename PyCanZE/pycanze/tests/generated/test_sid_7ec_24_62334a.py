from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62334a():
    client = ReplayUDSClient(sid_responses={"22334A": ['0762334A000188DE']})
    assert client.read_field("7ec.24.62334a") == pytest.approx(100574.0)
