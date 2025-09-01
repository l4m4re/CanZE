from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_24_623473():
    client = ReplayUDSClient(sid_responses={"223473": ['05623473204EAAAA']})
    assert client.read_field("7ec.24.623473") == pytest.approx(0.827)
