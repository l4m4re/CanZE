from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_78_6121():
    client = ReplayUDSClient(sid_responses={"2121": ['101F6121B0C11E67', '2190EF0DB0078000', '2218017F8FF8CA80', '2303C21143000400', '2400000000000000']})
    assert client.read_field("76d.78.6121") == pytest.approx(0.0)
