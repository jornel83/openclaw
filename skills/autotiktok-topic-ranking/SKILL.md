---
name: autotiktok-topic-ranking
description: Score and rank TikTok topic candidates for the AutoTikTok project. Use when defining or updating eight-dimension feature scoring, ranking weights, rerank rules, score outputs, module-2 schemas, prediction runs, or ranking fixtures.
---

# AutoTikTok Topic Ranking

Use this skill when the task is about converting structured topic candidates into ranked recommendations.

## What This Skill Owns

- module-2 input and output contracts
- eight-dimension feature scoring
- ranking weights and profile selection
- rerank logic
- score explanations and risk flags
- `topicScore`
- `predictionRun`

## Read First

- Read [references/scoring-system.md](references/scoring-system.md) for the eight-dimension model, weight profiles, and rerank intent.
- Read [references/feature-score-rubric.md](references/feature-score-rubric.md) for the first-pass deterministic scoring rubric behind the dry-run runner.
- Read [references/ranking-contracts.md](references/ranking-contracts.md) for input and output contracts, fixture inventory, and contract freeze points.
- Read [references/ranking-delivery.md](references/ranking-delivery.md) for the ranking owner scope, milestone order, and integration checkpoints.
- Read [references/ranking-dry-run.md](references/ranking-dry-run.md) for the local runner flow, sample outputs, and expected artifacts.

## Working Rules

- Score `topicCandidate`, not individual hot videos.
- Keep feature construction and score aggregation explainable.
- Preserve `searchEvidence` and `executionProfile` as first-class ranking inputs.
- Prefer deterministic logic and configuration over opaque freeform model decisions.
- Do not redesign signal collection here unless the ranking contract cannot be satisfied otherwise.

## Output Expectations

Ranking work should usually end with one or more of these:

- a schema or fixture update for ranking inputs or outputs
- a feature-builder rule
- a scoring profile update
- a rerank rule
- a `topicScore` or `predictionRun` example

## Bundled Script

- Run `python3 {baseDir}/scripts/validate_ranking_fixtures.py` to validate the default discovery-driven ranking input plus the shared ranking fixtures and profile weights.
- Pass `--candidates`, `--context`, `--profiles`, or `--rubric` to point at alternate fixture files.
- Run `python3 {baseDir}/scripts/dry_run_ranking.py` to score the committed discovery artifact and produce ranked sample outputs.
- Run `python3 {baseDir}/scripts/ranking_profile_matrix.py` to replay the same candidates across `growth`, `scale`, and `search_priority` stage modes and compare ranking behavior.
- The profile-matrix runner defaults to `skills/autotiktok/fixtures/scoring-context-matrix.fixture.json` so stage-specific assumptions stay visible and editable in data, not hidden in code.
- Use `python3 skills/autotiktok/scripts/validate_ranking_optimizer_contract.py` when you want to confirm ranking output still satisfies the fields and invariants consumed by the optimizer layer.
- Use `python3 skills/autotiktok/scripts/validate_ranking_profile_matrix_expectations.py` when you want a behavioral gate that checks the intended stage-mode differences, not just JSON alignment.
- By default `--profile-id auto` resolves from `scoringContext.stageMode`.
- Pass `--profile-id`, `--snapshot-id`, `--run-id`, `--rubric`, or `--output` when you want a different profile or want to write a sample result file.
- The deterministic scoring core now lives in `scripts/ranking_lib.py`, while `config/feature-rubric.v1.json` holds the first-pass feature and rerank parameters.

## Related Skills

- Use `autotiktok-topic-discovery` for upstream candidate generation.
- Use `autotiktok-strategy-optimizer` for outcome backfill, reward, and daily or weekly optimization loops.
