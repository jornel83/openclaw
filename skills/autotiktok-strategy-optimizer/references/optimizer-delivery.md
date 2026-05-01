# Optimizer Delivery

This reference extracts the optimizer-relevant parts of the shared development plan.

## Primary Owner Scope

Optimizer work maps to the shared module-2 and evaluation owner scope:

- outcome backfill
- eval runs
- reward logic
- daily review
- shadow challengers
- weekly promotion

## Milestone Order

### Week 1

Freeze these evaluation-side contracts early:

- `predictionRun`
- `topicOutcomeBackfill`
- reward assumptions that later comparisons depend on

### Week 5

The system should be able to:

- replay historical runs
- attach backfilled outcomes
- compute first-pass evaluation metrics

### Week 6

The system should be able to:

- produce daily diagnostics
- compare shadow challengers
- prepare a weekly promotion decision

## Healthy Integration Signals

- replay is stable across fixture and snapshot runs
- reward uses normalized metrics
- topic reward and performance reward are reported separately
- weekly promotion remains stricter than daily experimentation

## Main Risks

- overfitting to short-window feedback
- reward confusion between topic quality and execution quality
- promotion pressure causing unstable champion churn
- missing outcome coverage reducing signal quality

## Related Shared Docs

- Shared delivery plan: [../../autotiktok/docs/development-plan.md](../../autotiktok/docs/development-plan.md)
