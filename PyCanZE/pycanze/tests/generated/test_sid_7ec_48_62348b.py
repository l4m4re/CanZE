from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_48_62348b():
    client = ReplayUDSClient(sid_responses={"22348B": ['103F62348B00E000', '2100E00000E00000', '22E00000E00000E0', '230000E00000E000', '2400E00000E00000', '25E00000E00000E0', '260000E00000E000', '2700E00000E00000', '28E00000E00000E0', '2900AAAAAAAAAAAA']})
    assert client.read_field("7ec.48.62348b") == pytest.approx(57344.0)
