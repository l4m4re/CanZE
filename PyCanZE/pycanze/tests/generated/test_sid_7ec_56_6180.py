# string
from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_56_6180():
    client = ReplayUDSClient(sid_responses={"2180": ['101A618030323735', '2152263030313030', '2235345202040AB0', '23139101010188AA']})
    assert client.read_field("7ec.56.6180") == '26'
