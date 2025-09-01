from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_48_6104():
    client = ReplayUDSClient(sid_responses={"2104": ['104D610408633F08', '21673F086A3F0864', '223F08533F084F3F', '23084340082D4008', '248E3E08803E0875', '253E082940FFFFFF', '26FFFFFFFFFFFFFF', '27FFFFFFFFFFFFFF', '28FFFFFFFFFFFFFF', '29FFFFFFFFFFFFFF', '2AFFFFFFFFFF3E3F', '2B40000000000000']})
    assert client.read_field("76d.48.6104") == pytest.approx(0.0)
