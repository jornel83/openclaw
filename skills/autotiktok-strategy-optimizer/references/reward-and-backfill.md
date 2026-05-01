# Reward and Backfill

This reference narrows the shared plan to evaluation and reward logic.

The current runnable policy config lives at:

- [../config/optimizer-policy.v1.json](../config/optimizer-policy.v1.json)

The reusable optimizer implementation lives at:

- [../scripts/optimizer_lib.py](../scripts/optimizer_lib.py)

## Two-Layer Evaluation Model

The shared plan now uses two layers:

- topic opportunity evaluation
- post-performance evaluation

The topic layer remains primary. Post-performance only enhances the final reward.

## Topic Layer Metrics

Primary topic metrics:

- `Hit@3`
- `Hit@10`
- `NDCG@10`
- `DupRate`
- `TypeCoverage`
- `Novelty`
- `ExecutableRate`

## Topic Reward

```text
TopicReward =
  0.30*Hit@3 +
  0.20*NDCG@10 +
  0.15*Hit@10 +
  0.10*Novelty +
  0.10*TypeCoverage +
  0.10*ExecutableRate -
  0.15*DupRate
```

## Performance Layer

When real post data exists, prefer normalized performance metrics:

- `ViewLift`
- `RetentionProxy`
- `ShareSaveProxy`
- `FollowConversionProxy`

For MVP, only `ViewLift` may be available.

## Performance Reward

```text
PerformanceReward =
  0.50*ViewLift +
  0.20*RetentionProxy +
  0.15*ShareSaveProxy +
  0.15*FollowConversionProxy
```

Fallback:

```text
PerformanceRewardMvp = ViewLift
```

## Combined Reward

```text
CombinedReward =
  TopicReward * (1 - PerformanceWeight) +
  PerformanceReward * PerformanceWeight
```

Recommended defaults:

- `PerformanceWeight <= 0.15`
- `PerformanceWeight = 0` when no real post data exists

## Backfill Windows

Evaluate each prediction run on:

- `t+1`
- `t+3`
- optional `t+7`

Backfill should capture:

- future search lift
- future video density
- future content-gap persistence
- normalized post-performance signals when available

## Why Views Are Enhancement Only

Raw views are too noisy to become the sole truth because they mix:

- topic quality
- execution quality
- hook strength
- edit quality
- timing effects
- account volatility
