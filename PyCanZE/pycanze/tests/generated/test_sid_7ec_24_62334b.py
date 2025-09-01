from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_62334b():
    client = ReplayUDSClient(sid_responses={"22334B": ['0762334B005C10D4']})
    assert client.read_field("7ec.24.62334b") == pytest.approx(6033620.0)
