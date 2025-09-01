from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76e_32_62200b():
    client = ReplayUDSClient(sid_responses={"22200B": ['100A62200B0B0C0E', '21111317000B0C0E']})
    assert client.read_field("76e.32.62200b") == pytest.approx(12.0)
