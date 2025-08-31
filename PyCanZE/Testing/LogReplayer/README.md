# Java log replayer

A minimal standalone Java utility can convert raw ELM327 dumps into a JSON
array of decoded field values. Each entry contains the field SID, human
readable name, numeric value and unit.

## Build

From the repository root with a JDK installed:

```bash
javac -d PyCanZE/Testing/LogReplayer PyCanZE/Testing/LogReplayer/LogReplayer.java
```

This creates class files under `PyCanZE/Testing/LogReplayer/lu/`, which are
ignored by Git and can be deleted after use.

## Usage

Replay a raw log and write the decoded JSON:

```bash
java -cp PyCanZE/Testing/LogReplayer lu.fisch.canze.tools.LogReplayer \
    PyCanZE/Testing/logs/zoe-ready-fullscan-20250831-175317.raw \
    PyCanZE/Testing/logs/zoe-ready-fullscan-20250831-175317.json
```

The JSON files in `PyCanZE/Testing/logs/` serve as canonical baselines for the
Python decoder.
