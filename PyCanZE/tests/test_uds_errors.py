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
