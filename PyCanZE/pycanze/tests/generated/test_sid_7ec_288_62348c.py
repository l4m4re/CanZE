from pycanze.replay_client import ReplayClient as ReplayUDSClient
import pytest

def test_7ec_288_62348c():
    client = ReplayUDSClient(sid_responses={"22348C": ['103F62348C3BC241', '213BBEFF3BBE953B', '22BE473BBD7E3BBD', '23503BBD113BBCB9', '243BBC983BBC8E3B', '25BC753BBC163BB8', '26E13BC37F3BC342', '273BC2D83BC2C63B', '28C2973BC26B3BC2', '295CAAAAAAAAAAAA']})
    assert client.read_field("7ec.288.62348c") == pytest.approx(3914774.0)
