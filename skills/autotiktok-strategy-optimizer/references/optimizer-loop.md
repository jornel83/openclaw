# Optimizer Loop

This reference extracts the aggressive optimization loop from the shared plan.

## Core Principle

The plan allows faster iteration, but not daily full promotion.

Target cadence:

- daily optimization
- daily review
- weekly formal promotion

## Champion and Shadow Challengers

Use two layers:

- champion:
  - the stable version used by the daily production run
- shadow challengers:
  - candidate profiles and prompt variants evaluated offline

## Daily Review

Daily review may:

- analyze fresh `t+1` feedback
- consume available `t+3` feedback
- preserve ranking profile-selection provenance so optimizer decisions remain replayable
- preserve candidate-source provenance so optimizer outputs can be traced back to discovery inputs
- consume challenger observations that already carry aggregated topic metrics and performance summaries
- inspect ranking-layer rejection and rerank pressure
- generate diagnostics
- compare challengers on replay and holdout sets
- update a shadow leaderboard

Daily review must not:

- replace the champion directly
- bypass evaluator gates
- change schemas or evaluator rules to win a comparison

## Weekly Promotion

Weekly promotion should:

- aggregate challenger results across the recent week
- prefer runs with `t+3` and optional `t+7` outcomes
- re-check the hidden holdout set
- promote only when reward improves and hard gates do not regress

## Daily Gates

Challengers should pass these gates before entering the shadow leaderboard:

- `ExecutableRate` stays acceptable
- `DupRate` stays within tolerance
- `TypeCoverage` does not collapse
- hidden holdout does not show clear regression

## Scheduling Model

The shared plan currently recommends:

- `cron D` for daily review and shadow challenger evaluation
- `cron E` for weekly formal promotion

The optimizer is explicitly time-triggered, not idle-triggered.

## Current Policy Surface

The runnable mock optimizer now keeps these knobs in one policy file:

- topic reward weights
- performance reward weights
- performance-weight caps
- realized-strength weights
- daily shadow gate tolerances
- weekly promotion thresholds

That policy currently lives in:

- [../config/optimizer-policy.v1.json](../config/optimizer-policy.v1.json)
