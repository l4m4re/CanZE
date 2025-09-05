import pytest

from pycanze.models import Field


FIELD = Field(
    sid="sid",
    frame_id=0x7EC,
    start_bit=0,
    end_bit=7,
    resolution=1.0,
    offset=0.0,
    decimals=0,
    unit="",
    request_id="222002",
    response_id="622002",
    options=0,
)

# The 29-bit examples below are synthetic. The replay database only contains
# traffic captured from a classic (11-bit) Zoe, so extended CAN ID support has
# not yet been exercised against real vehicle data.
FIELD_29 = Field(
    sid="sid29",
    frame_id=0x18DAF110,
    start_bit=0,
    end_bit=7,
    resolution=1.0,
    offset=0.0,
    decimals=0,
    unit="",
    request_id="22F190",
    response_id="62F190",
    options=0,
)


def test_unknown_sid_raises_key_error(mk_replay_client):
    client = mk_replay_client(fields={})
    with pytest.raises(KeyError):
        client.read_field("missing")


def test_negative_response_returns_none(mk_replay_client):
    client = mk_replay_client(sid_responses={"222002": ["7F2213"]}, fields={"sid": FIELD})
    assert client.read_field("sid") is None


def test_invalid_service_raises_value_error(mk_replay_client):
    bad_field = Field(
        sid="bad",
        frame_id=0x7EC,
        start_bit=0,
        end_bit=7,
        resolution=1.0,
        offset=0.0,
        decimals=0,
        unit="",
        request_id="232002",
        response_id=None,
        options=0,
    )
    client = mk_replay_client(fields={"bad": bad_field})
    with pytest.raises(ValueError):
        client.read_field("bad")


def test_negative_response_29bit_returns_none(mk_replay_client):
    client = mk_replay_client(
        sid_responses={"22F190": ["7F2213"]}, fields={"sid29": FIELD_29}
    )
    assert client.read_field("sid29") is None


def test_invalid_service_29bit_raises_value_error(mk_replay_client):
    bad_field = Field(
        sid="bad29",
        frame_id=0x18DAF110,
        start_bit=0,
        end_bit=7,
        resolution=1.0,
        offset=0.0,
        decimals=0,
        unit="",
        request_id="23F190",
        response_id=None,
        options=0,
    )
    client = mk_replay_client(fields={"bad29": bad_field})
    with pytest.raises(ValueError):
        client.read_field("bad29")
