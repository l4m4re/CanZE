# SID decoding reports

This directory hosts reports comparing decoded service identifiers (SIDs)
from Android log captures against the CSV definitions used by PyCanZE.

## `test_sid_decoding.py`

`test_sid_decoding.py` replays the logs and validates that decoded values
match the CSV definitions. The resulting reports list each SID alongside its
human‑readable name:

- `decoding_mismatches.txt` – SIDs that decoded to a different value than the
  CSV definition.
- `decoding_skipped_sids.txt` – SIDs present in the CSV but absent from all
  captured logs.

## Generated SID tests

`tools/generate_sid_tests.py` builds per-SID unit tests from the same logs.
SIDs that could not be converted into tests are written to
`generated/skipped_sids.txt` together with their CSV names.

`skipped_discrepancies.txt` compares the skipped SIDs reported by the
generator with those from the decoding test. All skipped SIDs originate
from the Java-generated JSON logs, meaning the Android app returned a
value even though the SID was not available in the Python CSV database.
This suggests the Android version contains additional hard-coded
definitions or the CSV set is incomplete.
