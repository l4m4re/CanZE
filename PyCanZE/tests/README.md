# Debugging SID decoding

This directory documents a quick workflow for investigating decoding issues
using the captured vehicle logs.

1. **Regenerate per-SID tests**
   ```bash
   python PyCanZE/tools/generate_sid_tests.py --overwrite
   ```
   The script writes tests under `pycanze/tests/generated/` and lists missing
   SIDs in `skipped_sids.txt`.

2. **Run the tests**
   ```bash
   PYTHONPATH=PyCanZE pytest PyCanZE/pycanze/tests/generated -q
   ```
   Failures highlight decoders that disagree with the log data.

3. **Refresh decoder summaries**
   ```bash
   python - <<'PY'
   import importlib, pathlib
   m = importlib.import_module('PyCanZE.Testing.sid_decoding.test_sid_decoding'.replace('/', '.'))
   out = pathlib.Path('PyCanZE/Testing/sid_decoding/decoding_mismatches.txt')
   with out.open('w') as f:
       if not m.MISMATCHES:
           f.write('No mismatches.\n')
       else:
           for sid,(exp,got,unit,name) in sorted(m.MISMATCHES.items()):
               f.write(f"{sid}\t{exp}\t{got}\t{unit or ''}\t{name or ''}\n")
   out2 = pathlib.Path('PyCanZE/Testing/sid_decoding/decoding_skipped_sids.txt')
   with out2.open('w') as f:
       if not m.SKIPPED_SIDS:
           f.write('')
       else:
           for sid,name in sorted(m.SKIPPED_SIDS.items()):
               f.write(f"{sid}\t{name}\n")
   PY
   ```
   The resulting text files provide a concise list of mismatches and skipped
   SIDs for regression tracking.

4. **Iterate** – adjust decoders, rerun the tests and regenerate the summaries
   until the mismatches are resolved.

