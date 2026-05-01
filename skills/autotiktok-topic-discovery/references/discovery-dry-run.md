# Discovery Dry Run

This reference explains the mock discovery runner shipped with the discovery skill.

## Purpose

The discovery dry-run runner is the first executable scaffold for module 1.

It is designed to answer:

- can we start from signal-level inputs instead of prebuilt candidates?
- can we package evidence bundles deterministically?
- can we expose merge groups explicitly?
- can we emit candidates that already satisfy the shared discovery contract?

## Input

The committed discovery ingest seam is now split into 3 standalone artifacts:

- [../fixtures/source-snapshots.sample.json](../fixtures/source-snapshots.sample.json)
- [../fixtures/signal-items.sample.json](../fixtures/signal-items.sample.json)
- [../fixtures/video-samples.sample.json](../fixtures/video-samples.sample.json)

Those inputs materialize into:

- [../fixtures/discovery-snapshot-materialization.sample.json](../fixtures/discovery-snapshot-materialization.sample.json)

Build that materialization with:

```bash
python3 {baseDir}/scripts/build_discovery_snapshot_materialization.py
```

Validate the committed materialization with:

```bash
python3 {baseDir}/scripts/validate_discovery_snapshot_materialization.py
python3 skills/autotiktok/scripts/validate_discovery_snapshot_ingest_alignment.py
```

The legacy compatibility input still exists at:

- [../fixtures/raw-signals.sample.json](../fixtures/raw-signals.sample.json)

Validate that compatibility fixture with:

```bash
python3 {baseDir}/scripts/validate_raw_signals.py
```

## Output

The runner writes or prints a payload containing:

- `normalizedSignals`
- `topicAbstractions`
- `evidenceBundles`
- `mergeGroups`
- `candidates`

The merge / packaging layer now also freezes:

- `mergeClassification`
- `dedupeDecision`
- `searchEvidenceSummary`
- `executionEvidenceSummary`
- `packagingReadiness`

The committed sample output lives at:

- [../fixtures/discovery-dry-run.sample.json](../fixtures/discovery-dry-run.sample.json)

That committed sample is now treated as a derived artifact from the standalone snapshot inputs, the built snapshot-materialization artifact, and the current discovery policy.

## What The Runner Does

1. loads standalone snapshot inputs or an explicit materialized fixture
2. materializes `sourceSnapshots + signalItems + videoSamples` into the snapshot-materialization contract
3. adapts that materialized payload into the raw-signal shape used by the packaging core
4. normalizes signal text into deterministic `normalizedSignals`
5. resolves one `topicAbstraction` per stable `topicFingerprint`
6. groups signals by `topicFingerprint`
7. builds evidence bundles
8. emits merge-group metadata
9. packages final candidates

## What The Runner Does Not Do

- it does not scrape real sources
- it does not do semantic clustering with a model
- it does not replace later module-1 implementation

It is a deterministic packaging scaffold for local iteration.

## Common Commands

```bash
python3 {baseDir}/scripts/discovery_dry_run.py
python3 {baseDir}/scripts/discovery_dry_run.py --output {baseDir}/fixtures/discovery-dry-run.sample.json
python3 {baseDir}/scripts/build_discovery_snapshot_materialization.py --output {baseDir}/fixtures/discovery-snapshot-materialization.sample.json
python3 {baseDir}/scripts/discovery_dry_run.py --input /tmp/other-materialization.json
python3 {baseDir}/scripts/discovery_dry_run.py --source-snapshots /tmp/source-snapshots.json --signal-items /tmp/signal-items.json --video-samples /tmp/video-samples.json
python3 {baseDir}/scripts/discovery_dry_run.py --signals /tmp/other-raw-signals.json
```
