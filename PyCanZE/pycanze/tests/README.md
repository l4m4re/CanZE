# SID decoding tests

This directory contains generated SID unit tests built from Android log captures.

## Generated SID tests

`tools/generate_sid_tests.py` builds a single parametrized test from the logs. SIDs that could not be converted into tests are written to `generated/skipped_sids.txt` along with their CSV names.

An exhaustive log-replay harness remains available under `Testing/sid_decoding/test_sid_decoding.py` for manual verification. Running that script will produce detailed mismatch reports but it is not part of the default test suite.
