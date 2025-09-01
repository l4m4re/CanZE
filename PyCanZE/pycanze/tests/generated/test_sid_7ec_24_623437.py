from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623437():
    client = ReplayUDSClient(sid_responses={"223437": ['04623437FEAAAAAA']})
    assert client.read_field("7ec.24.623437") == pytest.approx(508.0)
