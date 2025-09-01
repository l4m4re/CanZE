from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_24_622018():
    client = ReplayUDSClient(sid_responses={"222018": ['0762201800000000']})
    assert client.read_field("76e.24.622018") == pytest.approx(0.0)
