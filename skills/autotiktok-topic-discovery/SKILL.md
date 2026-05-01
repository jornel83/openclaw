---
name: autotiktok-topic-discovery
description: Discover and package TikTok topic candidates from trend, search, and public-video signals. Use when defining or refining signal ingestion, topic abstraction, candidate generation, dedupe and merge rules, search-evidence packaging, execution-profile packaging, or module-1 delivery scope for the AutoTikTok project.
---

# AutoTikTok Topic Discovery

Use this skill when the task is about turning raw TikTok signals into structured topic candidates.

## What This Skill Owns

- signal-source strategy
- snapshot-based collection assumptions
- `signal -> evidence_bundle -> topic_candidate`
- topic abstraction and merge behavior
- `topicFingerprint`
- `searchEvidence`
- `executionProfile`

## Read First

- Read [references/discovery-scope.md](references/discovery-scope.md) for signal strategy, collector boundaries, storage objects, and module-1 pipeline shape.
- Read [references/video-sample-contract.md](references/video-sample-contract.md) when you need the current collector-facing field contract for `videoSamples`.
- Read [references/topic-candidate-contract.md](references/topic-candidate-contract.md) for the discovery-owned `topicCandidate` contract and freeze checklist.
- Read [references/merge-and-evidence.md](references/merge-and-evidence.md) for the current merge, dedupe, and evidence-packaging rules.
- Read [references/discovery-dry-run.md](references/discovery-dry-run.md) for the mock discovery runner, sample signal inputs, and generated artifacts.
- Read [references/discovery-delivery.md](references/discovery-delivery.md) for owner split, milestones, and integration risks.
- Read [../autotiktok/docs/热门题材策略模块开发需求.md](../autotiktok/docs/热门题材策略模块开发需求.md) when you need the original product framing for candidate generation.

## Working Rules

- Keep module boundaries strict:
  - discovery produces `topicCandidate`
  - ranking consumes `topicCandidate`
- Treat official TikTok web products as the primary signal source.
- Keep outputs snapshot-based so replay and offline evaluation remain possible.
- Preserve evidence chains instead of collapsing candidates into freeform titles.
- Do not design ranking weights or reward logic here unless the discovery output contract must change.

## Output Expectations

Discovery work should usually end with one or more of these:

- a candidate schema change proposal
- a merge or dedupe rule
- a snapshot or collector requirement
- a fixture or evidence-packaging update

## Bundled Script

- Run `python3 {baseDir}/scripts/validate_raw_signals.py` to validate the raw-signal fixture shape before packaging.
- Pass `--input <path>` to validate another raw-signal fixture file.
- Run `python3 {baseDir}/scripts/validate_discovery_snapshot_materialization.py` to validate the snapshot-materialization fixture that discovery now uses by default.
- Pass `--input <path>` to validate another snapshot-materialization fixture file.
- Run `python3 {baseDir}/scripts/build_discovery_snapshot_materialization.py` when you want to materialize `sourceSnapshots + signalItems + videoSamples` into the committed snapshot-materialization artifact.
- Run `python3 {baseDir}/scripts/check_topic_candidate_contract.py` to validate the shared candidate fixture against the discovery-owned contract.
- Pass `--input <path>` to validate another candidate fixture file.
- Run `python3 {baseDir}/scripts/discovery_dry_run.py` to turn a snapshot-materialization or raw-signal input into evidence bundles, merge groups, and packaged candidates.
- The committed discovery output now also freezes `normalizedSignals` and `topicAbstractions`, so normalization / abstraction regressions can be checked before ranking starts.
- The committed discovery output now also freezes merge / packaging semantics such as `mergeClassification`, `dedupeDecision`, `searchEvidenceSummary`, and `executionEvidenceSummary`, so merge regressions can be checked before ranking starts.
- Pass `--input <path>`, `--signals <path>`, `--source-snapshots <path>`, `--signal-items <path>`, `--video-samples <path>`, `--policy <path>`, or `--output <path>` to replay another discovery input fixture or write a sample artifact file.
- The reusable discovery core now lives in `scripts/discovery_lib.py`, while `config/discovery-policy.v1.json` holds source-priority, merge, and packaging knobs.

## Related Skills

- Use `autotiktok-topic-ranking` for feature scoring, ranking, rerank, and score outputs.
- Use `autotiktok-strategy-optimizer` for reward, backfill, daily review, and champion/challenger work.
