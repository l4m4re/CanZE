from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_76d_16_6104():
    client = ReplayUDSClient(sid_responses={"2104": ['104D610408703E08', '21733E08763E0870', '223E08613F08603F', '2308533F083C4008', '249A3E088B3E088A', '253E083840FFFFFF', '26FFFFFFFFFFFFFF', '27FFFFFFFFFFFFFF', '28FFFFFFFFFFFFFF', '29FFFFFFFFFFFFFF', '2AFFFFFFFFFF3E3E', '2B40000000000000']})
    assert client.read_field("76d.16.6104") == pytest.approx(0.0)
