# Discovery Scope

This reference narrows the shared AutoTikTok plan down to the discovery skill only.

## What Discovery Owns

- signal-source strategy
- collector split and snapshot assumptions
- storage objects needed before ranking
- topic abstraction
- candidate expansion
- merge and dedupe
- evidence-preserving packaging

## Core Goal

Discovery is not trying to pick the final winner. Its job is to convert platform signals into a stable set of structured topic candidates that ranking can score.

## Recommended Signal Strategy

- Use official TikTok web products as primary sources:
  - Creative Center
  - Creator Search Insights
- Use public TikTok video sampling as an evidence enhancer, not the source of truth.
- Freeze everything into time-sliced snapshots so later replay is possible.

## Collector Split

Use three collectors with clear ownership:

- `collector_creative_center`
- `collector_search_insights`
- `collector_public_tiktok`

Each collector should emit raw source outputs that can be traced back to a specific snapshot.

For the current collector-facing video field contract, read:

- [video-sample-contract.md](video-sample-contract.md)

## Discovery Storage Objects

Discovery work should preserve these object layers:

- `sourceSnapshots`
- `signalItems`
- `videoSamples`
- `evidenceBundle`
- `topicCandidate`

Discovery should also preserve a stable `topicFingerprint` so downstream evaluation can connect future outcomes back to the original candidate.

## Pipeline Shape

The shared plan defines discovery as this pipeline:

1. `Signal Ingestion`
2. `Normalization`
3. `Topic Abstraction`
4. `Candidate Expansion`
5. `Merge & Dedupe`
6. `Tagging & Packaging`

## Discovery Principles

- `source-grounded`
- `abstract-not-copy`
- `merge-before-rank`
- `evidence-preserved`

## Boundary With Ranking

Discovery stops after a `topicCandidate` is fully packaged.

Discovery owns:

- evidence quality
- topic abstraction quality
- merge behavior
- search evidence packaging
- execution profile packaging

Ranking owns:

- feature construction
- weights
- rerank
- score explanation

## Related Shared Docs

- Shared master plan: [../../autotiktok/docs/technical-plan.md](../../autotiktok/docs/technical-plan.md)
- Shared delivery plan: [../../autotiktok/docs/development-plan.md](../../autotiktok/docs/development-plan.md)
