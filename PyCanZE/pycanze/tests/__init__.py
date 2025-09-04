from __future__ import annotations

from typing import Callable, Mapping, Sequence

import pytest

from pycanze.models import Field
from pycanze.replay_client import ReplayClient


@pytest.fixture
def mk_replay_client() -> Callable[[Mapping[str, Sequence[str]]], ReplayClient]:
    """Factory yielding :class:`ReplayClient` preloaded with common fields."""

    fields = {
        "soc": Field(
            sid="soc",
            frame_id=0x7EC,
            start_bit=24,
            end_bit=39,
            resolution=1.0,
            offset=0.0,
            decimals=0,
            unit="%",
            request_id="222002",
            response_id=None,
            options=0,
        ),
        "pump": Field(
            sid="pump",
            frame_id=0x7EC,
            start_bit=24,
            end_bit=31,
            resolution=1.0,
            offset=0.0,
            decimals=0,
            unit="%",
            request_id="223319",
            response_id=None,
            options=0,
        ),
    }

    def _factory(responses: Mapping[str, Sequence[str]]) -> ReplayClient:
        return ReplayClient(sid_responses=responses, fields=fields)

    return _factory
