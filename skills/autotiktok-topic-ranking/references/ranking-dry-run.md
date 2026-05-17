# Ranking Dry Run

This reference explains the local dry-run script shipped with the ranking skill.

## Purpose

The dry-run runner is the first executable ranking skeleton for this project.

It is designed to answer:

- can the current discovery artifact be parsed into ranking inputs?
- can we build a deterministic first-pass feature vector?
- can we aggregate scores with the current profile weights?
- can we emit `topicScore` and `predictionRun` examples?

## Inputs

By default the runner reads the committed discovery artifact plus the shared ranking fixtures:

- [../../autotiktok-topic-discovery/fixtures/discovery-dry-run.sample.json](../../autotiktok-topic-discovery/fixtures/discovery-dry-run.sample.json)
- [../../autotiktok/fixtures/topic-candidates.fixture.json](../../autotiktok/fixtures/topic-candidates.fixture.json)
- [../../autotiktok/fixtures/scoring-context.fixture.json](../../autotiktok/fixtures/scoring-context.fixture.json)
- [../../autotiktok/fixtures/scoring-context-matrix.fixture.json](../../autotiktok/fixtures/scoring-context-matrix.fixture.json)
- [../../autotiktok/fixtures/scoring-profiles.fixture.json](../../autotiktok/fixtures/scoring-profiles.fixture.json)

## Default Output

Without `--output`, the runner prints a JSON payload to stdout containing:

- `candidateSource`
- `scores`
- `predictionRun`
- `rankingSummary`

## Sample Output File

The committed sample output lives at:

- [../fixtures/ranking-dry-run.sample.json](../fixtures/ranking-dry-run.sample.json)
- [../fixtures/ranking-profile-matrix.sample.json](../fixtures/ranking-profile-matrix.sample.json)

This file is useful when:

- reviewing the current heuristic scorer
- checking whether profile changes change order
- comparing future challengers against a baseline output shape
- inspecting rerank penalties and rejection decisions

## Common Commands

```bash
python3 {baseDir}/scripts/dry_run_ranking.py
python3 {baseDir}/scripts/dry_run_ranking.py --profile-id search-priority-default
python3 {baseDir}/scripts/dry_run_ranking.py --output {baseDir}/fixtures/ranking-dry-run.sample.json
python3 {baseDir}/scripts/ranking_profile_matrix.py --output {baseDir}/fixtures/ranking-profile-matrix.sample.json
```

For a user-facing AutoTikTok report with downloaded / understood MP4 evidence,
render the score table through the report helper so the table includes the local
video filename:

```bash
python3 {baseDir}/scripts/build_ranking_report.py \
  --ranking <ranking-dry-run.json> \
  --discovery <discovery-dry-run.json> \
  --video-content-analysis <video-content-analysis.json> \
  --output <report.md>
```

The generated table has a `视频文件` column. It uses `ranking-dry-run.json` for
rank and score order, `discovery-dry-run.json` for topic-to-video-sample
evidence, and `video-content-analysis.json` for `videoPath`. Only the filename
is rendered in the table, not the full local path.

With no explicit profile, the runner resolves the profile from `scoringContext.stageMode`.

The runner also records where the candidate input came from, for example:

- a direct discovery artifact
- the shared derived candidates fixture
- a standalone candidate fixture

The profile-matrix runner uses the same inputs, but emits a compact cross-stage comparison instead of a single full ranking payload.
Its default stage contexts come from `scoring-context-matrix.fixture.json`, so cross-stage assumptions can be inspected and edited without patching the runner.

For semantic regression checks on that matrix, use:

```bash
python3 skills/autotiktok/scripts/validate_ranking_profile_matrix_expectations.py
```

## What The Runner Does

1. loads the committed discovery artifact plus the ranking-owned context/profile fixtures
2. builds an 8-dimension feature vector per topic
3. computes weighted total score
4. maps the result into:
   - `priorityLevel`
   - `recommendedUse`
   - `riskFlags`
   - `nextAction`
   - `isRejected`
5. applies a rerank pass with explicit penalties and diagnostics
6. records candidate-source provenance
7. emits a `predictionRun`

The shared `topic-candidates.fixture.json` file now remains as a derived compatibility artifact, not the default ranking source of truth.

## What The Runner Does Not Do

- it does not claim production-grade model quality
- it does not replace later optimizer work
- it does not infer missing upstream evidence magically

It is a deterministic scaffold meant to unblock ranking development.
