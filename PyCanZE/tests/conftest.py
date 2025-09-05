import pytest

from pycanze.replay_client import ReplayClient
from pycanze.models import Field


@pytest.fixture
def mk_replay_client():
    """Factory to build ReplayClient instances with canned responses."""

    def _mk(*, responses=None, sid_responses=None, fields=None):
        return ReplayClient(responses=responses, sid_responses=sid_responses, fields=fields)

    return _mk
