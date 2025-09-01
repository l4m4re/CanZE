from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_24_622021():
    client = ReplayUDSClient(sid_responses={"222021": ['04622021021E643C']})
    assert client.read_field("76e.24.622021") == pytest.approx(2.0)
